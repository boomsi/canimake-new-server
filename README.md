# CanIMake API

基于 FastAPI 的后端服务，用于集成大模型、MCP 和 RAG。

## 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   - 复制 `.env.example` 到 `.env`
   - 填写你的 `DASHSCOPE_API_KEY`

3. **运行服务**
   ```bash
   python run.py
   ```

## 接口文档

服务启动后，可以访问以下地址查看自动生成的 API 文档：
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 当前功能

- [x] 基于 FastAPI 的工程初始化
- [x] 集成千问 (Qwen) 大模型接口
- [x] **灵感厨房 (Inspiration Kitchen)**: 专属 System Prompt 及菜谱生成接口 (`/api/v1/kitchen/recipes`)
- [ ] 集成 MCP (Model Context Protocol)
- [ ] 实现 RAG (Retrieval-Augmented Generation)
