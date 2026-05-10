"""
P0-1 后端 API 验证脚本
验证项: 登录、文章 CRUD、AI continue/polish/generate
运行: cd backend && python3 main.py (另一个终端) 然后 python3 tests/verify_api.py
"""
import requests
import json
import sys

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} — {detail}")


def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


# ============================================================
# 0. 准备: 重置 admin 密码为 admin123
# ============================================================
section("0. 准备")

import sqlite3
import bcrypt
from pathlib import Path

db_path = Path(__file__).parent.parent / "backend" / "blog.db"
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    expected_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    conn.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (expected_hash,))
    conn.commit()
    conn.close()
    check("重置 admin 密码为 admin123 (bcrypt)", True)
else:
    check("数据库文件存在", False, f"{db_path} 不存在")


# ============================================================
# 1. 登录
# ============================================================
section("1. 登录")

# 1a. 正确密码登录
r = requests.post(f"{BASE}/api/login", json={"username": "admin", "password": "admin123"})
check("admin/admin123 能登录", r.status_code == 200, f"status={r.status_code}")
token = r.json().get("access_token") if r.status_code == 200 else ""
check("返回 access_token", bool(token), f"token={token[:20]}..." if token else "empty")

# 1b. 错误密码
r = requests.post(f"{BASE}/api/login", json={"username": "admin", "password": "wrong"})
check("错误密码被拒绝", r.status_code == 401, f"status={r.status_code}")

# 1c. token 有效性
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(f"{BASE}/api/me", headers=headers)
check("token 有效，/api/me 返回 logged_in=true",
      r.status_code == 200 and r.json().get("logged_in") is True,
      f"status={r.status_code}, body={r.text}")

# 1d. 无 token 访问受保护端点
r = requests.post(f"{BASE}/api/posts", json={"title": "t", "content": "c", "tags": []})
check("无 token 创建文章返回 401", r.status_code == 401, f"status={r.status_code}")


# ============================================================
# 2. 文章 CRUD
# ============================================================
section("2. 文章 CRUD")

# 2a. 创建
r = requests.post(f"{BASE}/api/posts", headers=headers,
                  json={"title": "验证测试文章", "content": "这是测试内容", "tags": ["test"]})
check("创建文章返回 201", r.status_code == 201, f"status={r.status_code}")
post_id = r.json().get("id") if r.status_code == 201 else None
check("返回文章 ID", post_id is not None, f"id={post_id}")
check("标题一致", r.json().get("title") == "验证测试文章")
check("内容一致", r.json().get("content") == "这是测试内容")
check("标签一致", r.json().get("tags") == ["test"])

# 2b. 读取
if post_id:
    r = requests.get(f"{BASE}/api/posts/{post_id}")
    check("读取文章返回 200", r.status_code == 200, f"status={r.status_code}")
    check("读取内容一致", r.json().get("content") == "这是测试内容")

    # 2c. 编辑
    r = requests.put(f"{BASE}/api/posts/{post_id}", headers=headers,
                     json={"title": "已编辑标题", "content": "已编辑内容", "tags": ["test", "edited"]})
    check("编辑文章返回 200", r.status_code == 200, f"status={r.status_code}")
    check("编辑后标题更新", r.json().get("title") == "已编辑标题")
    check("编辑后内容更新", r.json().get("content") == "已编辑内容")

    # 验证读取也是新内容
    r = requests.get(f"{BASE}/api/posts/{post_id}")
    check("重新读取拿到编辑后内容", r.json().get("title") == "已编辑标题")

    # 2d. 删除
    r = requests.delete(f"{BASE}/api/posts/{post_id}", headers=headers)
    check("删除文章返回 204", r.status_code == 204, f"status={r.status_code}")

    # 2e. 删除后读取 404
    r = requests.get(f"{BASE}/api/posts/{post_id}")
    check("删除后读取返回 404", r.status_code == 404, f"status={r.status_code}")
else:
    for name in ["读取文章返回 200", "读取内容一致", "编辑文章返回 200",
                  "编辑后标题更新", "编辑后内容更新", "重新读取拿到编辑后内容",
                  "删除文章返回 204", "删除后读取返回 404"]:
        check(name, False, "前置条件失败: 未获得 post_id")


# ============================================================
# 3. AI 功能 (SSE 流式)
# ============================================================
section("3. AI 功能")

def read_sse(url, payload, max_chunks=5):
    """读取 SSE 流，返回 (chunks, done, error)"""
    chunks = []
    done = False
    error = None
    try:
        r = requests.post(url, headers={**headers, "Content-Type": "application/json"},
                         json=payload, stream=True, timeout=30)
        if r.status_code != 200:
            return [], False, f"HTTP {r.status_code}: {r.text}"
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            data = json.loads(line[6:])
            if "error" in data:
                error = data["error"]
                break
            if data.get("done"):
                done = True
                break
            if "chunk" in data:
                chunks.append(data["chunk"])
                if len(chunks) >= max_chunks:
                    break
    except Exception as e:
        error = str(e)
    return chunks, done, error

# 3a. AI continue (via skill platform)
print("  测试 AI continue_writing skill (可能需要等待 API 响应)...")
chunks, done, error = read_sse(f"{BASE}/api/ai/skills/continue_writing",
                                {"content": "今天天气很好，"})
check("AI continue_writing 返回 chunk", len(chunks) > 0, f"chunks={len(chunks)}, error={error}")
if chunks:
    print(f"    续写前几段: {''.join(chunks[:3])[:80]}...")

# 3b. AI polish (via skill platform)
print("  测试 AI polish skill...")
chunks, done, error = read_sse(f"{BASE}/api/ai/skills/polish",
                                {"selected_text": "这个东西很好用。", "content": "测试"})
check("AI polish 返回 chunk", len(chunks) > 0, f"chunks={len(chunks)}, error={error}")
if chunks:
    print(f"    润色结果前几段: {''.join(chunks[:3])[:80]}...")

# 3c. AI generate (via skill platform)
print("  测试 AI generate_article skill...")
chunks, done, error = read_sse(f"{BASE}/api/ai/skills/generate_article",
                                {"topic": "测试主题"})
check("AI generate_article 返回 chunk", len(chunks) > 0, f"chunks={len(chunks)}, error={error}")
if chunks:
    print(f"    生成文章前几段: {''.join(chunks[:3])[:80]}...")


# ============================================================
# 汇总
# ============================================================
print(f"\n{'='*50}")
print(f"  结果: {PASS} PASS / {FAIL} FAIL")
print(f"{'='*50}")
sys.exit(1 if FAIL > 0 else 0)
