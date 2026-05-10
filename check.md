# Check — 人工验证清单

## 待验证

- [ ] **密码持久性** — 改密码后重启服务，用新密码登录，确认不会被重置回默认值
- [ ] **默认密码警告** — 终端运行 `cd backend && python3 main.py`，不设置 ADMIN_PASSWORD，观察输出是否有 WARNING 提示
- [ ] **JWT 随机生成** — 同上，不设置 JWT_SECRET，观察输出是否有 JWT 相关警告
