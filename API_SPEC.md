# CanIMake API 接口文档

本文档包含了当前项目的所有 API 路由，方便开发者或 AI 获取接口详情。

## 通用响应格式
所有接口均返回以下统一 JSON 格式：
```json
{
  "code": 200,      // 200 表示成功，其他表示错误码
  "message": "success",
  "data": { ... }   // 具体业务数据
}
```

---

## 1. 基础接口 (Root)

### 1.1 服务状态检核
- **地址**: `/`
- **方式**: `GET`
- **说明**: 检查 API 服务是否正在运行。
- **返回值示例**:
```json
{
  "message": "Welcome to CanIMake API",
  "status": "running"
}
```

---

## 2. 元数据接口 (Meta)
标签：`meta`

### 2.1 获取预设厨具列表
- **地址**: `/api/v1/meta/appliances`
- **方式**: `GET`
- **说明**: 获取系统预设的常用厨具列表。
- **示例参数**: 无
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": ["炒锅", "煎锅", "微波炉", "烤箱", "空气炸锅", "奶锅", "蒸屉"]
}
```

### 2.2 获取热门食材列表
- **地址**: `/api/v1/meta/ingredients/trending`
- **方式**: `GET`
- **说明**: 获取当前热门或推荐的食材列表。
- **示例参数**: 无
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": ["螺丝椒", "香葱", "鸡蛋", "西红柿", "土豆", "牛腩", "海白虾"]
}
```

---

## 3. 厨房核心接口 (Kitchen)
标签：`kitchen`

### 3.1 生成菜谱列表
- **地址**: `/api/v1/kitchen/recipes`
- **方式**: `POST`
- **说明**: 根据提供的食材和厨具，利用 AI 生成推荐菜谱。
- **请求参数示例**:
```json
{
  "ingredients": ["西红柿", "鸡蛋", "牛腩"],
  "appliances": ["炒锅", "电饭煲"]
}
```
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "recipes": [
      {
        "dish_name": "经典西红柿炖牛腩",
        "difficulty": "中等",
        "prep_time": "60分钟",
        "tags": ["家常菜", "高蛋白", "暖胃"],
        "nutrition": {
          "calories": "450kcal",
          "protein": "35g",
          "fat": "25g",
          "carbs": "10g"
        },
        "ingredients": {
          "main": ["牛腩 500g", "西红柿 3个"],
          "pantry_needed": ["油", "盐", "生姜", "料酒"]
        },
        "pre_prep": ["牛腩切块焯水", "西红柿去皮切块"],
        "steps": ["热锅凉油，下姜片爆香", "放入牛腩翻炒至变色", "加入西红柿块炒出汁", "加水没过食材，中小火炖煮50分钟"],
        "pro_tip": "西红柿一定要炒出油，颜色才漂亮。"
      }
    ]
  }
}
```

---

## 4. 语言模型接口 (LLM)
标签：`llm`

### 4.1 通用对话接口
- **地址**: `/api/v1/llm/chat`
- **方式**: `POST`
- **说明**: 直接与后台配置的 LLM 模型进行对话。
- **请求参数示例**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "简单的介绍一下如何煎牛排？"
    }
  ],
  "temperature": 0.7
}
```
- **返回值示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "result": "煎牛排的关键在于：1. 室温回温... 2. 擦干表面... 3. 大火热锅...",
    "usage": {
      "prompt_tokens": 20,
      "completion_tokens": 50,
      "total_tokens": 70
    }
  }
}
```
