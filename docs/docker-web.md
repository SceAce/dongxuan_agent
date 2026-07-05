# Docker Web 运行说明

## 本地环境

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env`，填写 `OPENAI_API_KEY`。

默认 OpenAI 兼容配置：

```env
OPENAI_BASE_URL=https://aivalux.com
OPENAI_MODEL=gpt-5.5
OPENAI_WIRE_API=responses
```

## 启动服务

```bash
docker compose up --build
```

Web UI 默认监听：

```text
http://localhost:8000
```

## 运行数据

本地 Python 运行默认使用：

```text
data/runtime/
```

Docker 运行为了兼容已有部署，仍挂载：

```text
./dongxuan-data:/data/dongxuan
```

`dongxuan-data/memory.json` 保存案例记忆，`dongxuan-data/audit.jsonl` 保存审计日志。审计日志记录密码指纹、动作名、案例 ID 和状态，不记录明文密码。

`.dongxuan/` 是历史本地运行目录，仍可作为 Codex auth/config 兼容位置。

## Cloudflared 提示

如果网络阻断 HTTP/2 over TCP，但允许 QUIC，可以显式使用 QUIC：

```bash
cloudflared tunnel --protocol quic run dongxuan
```

预检查里 TCP 端口 `7844` 的警告表示 HTTP/2 transport 不可用，不代表 tunnel 不能运行。浏览器刷新或快速切换页面时出现 `stream canceled` 通常是前端取消了旧请求。
