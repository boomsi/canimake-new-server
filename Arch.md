# 项目架构

## 技术栈
- **框架**: FastAPI
- **LLM**: DashScope (通义千问)
- **配置**: Pydantic Settings
- **服务器**: Uvicorn

## 目录结构
```
app/
├── main.py              # FastAPI 应用入口，全局异常处理，CORS
├── api/v1/
│   ├── api.py          # 路由聚合
│   └── endpoints/      # 具体端点实现
│       ├── kitchen.py  # 菜谱生成
│       ├── llm.py      # LLM 对话
│       └── meta.py     # 元数据（厨具、食材）
└── core/
    ├── config.py       # 配置管理（环境变量）
    ├── schemas.py      # 统一响应模型 IResponse
    ├── prompts.py      # LLM 提示词
    └── mock_data.py    # Mock 数据
```

## 核心设计
- **统一响应**: 所有接口返回 `IResponse[T]` 格式（code, message, data）
- **异常处理**: 全局异常处理器统一错误响应
- **Mock 模式**: 通过 `MOCK_LLM` 配置开关，支持离线开发
- **API 版本**: 使用 `/api/v1` 前缀，便于后续版本迭代

## 主要端点
- `/api/v1/kitchen/recipes` - 根据食材和厨具生成菜谱
- `/api/v1/llm/chat` - LLM 通用对话
- `/api/v1/meta/*` - 元数据接口（厨具列表、热门食材）
