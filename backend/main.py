import hashlib
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from database import init_db, list_posts, get_post, create_post, update_post, delete_post, list_tags, get_user, update_password

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)

app = FastAPI(title="Personal Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class PostCreate(BaseModel):
    title: str
    content: str
    tags: list[str] = []


class Post(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    created_at: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的凭证")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="凭证已过期或无效")


# --- Routes ---
@app.post("/api/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = get_user(data.username)
    if not user or hash_password(data.password) != user["password_hash"]:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenResponse(access_token=create_token(data.username))


@app.get("/api/me")
def me(username: str | None = Depends(get_current_user)):
    return {"logged_in": username is not None, "username": username}


@app.put("/api/password")
def change_password(data: ChangePasswordRequest, username: str = Depends(require_auth)):
    user = get_user(username)
    if not user or hash_password(data.old_password) != user["password_hash"]:
        raise HTTPException(status_code=400, detail="旧密码错误")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少6位")
    update_password(username, hash_password(data.new_password))
    return {"detail": "密码修改成功"}


@app.get("/api/posts")
def api_list_posts(
    tag: str | None = None,
    q: str | None = None,
) -> list[Post]:
    return list_posts(tag=tag, q=q)


@app.get("/api/posts/{post_id}")
def api_get_post(post_id: int) -> Post:
    post = get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/api/posts", status_code=201)
def api_create_post(data: PostCreate, username: str = Depends(require_auth)) -> Post:
    return create_post(data.title, data.content, data.tags)


@app.put("/api/posts/{post_id}")
def api_update_post(post_id: int, data: PostCreate, username: str = Depends(require_auth)) -> Post:
    post = update_post(post_id, data.title, data.content, data.tags)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/api/posts/{post_id}", status_code=204)
def api_delete_post(post_id: int, username: str = Depends(require_auth)):
    if not delete_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")


@app.get("/api/tags")
def api_list_tags() -> list[str]:
    return list_tags()


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), username: str = Depends(require_auth)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    filename = f"{uuid.uuid4().hex}{ext}"
    content = await file.read()
    (UPLOAD_DIR / filename).write_bytes(content)
    return {"url": f"/uploads/{filename}", "filename": filename}


app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
