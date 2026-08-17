# hello-world-fastapi

AI 工具孵化服务器 P8 验证项目 —— FastAPI Hello World。

## 接口

| 路径 | 说明 |
|------|------|
| `/` | 状态信息(主机名 / Python 版本 / 运行时长) |
| `/health` | 健康检查 `{"status": "ok"}` |

容器内监听 `0.0.0.0:8000`(Coolify Proxy 可访问)。
