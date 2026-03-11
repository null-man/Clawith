---
name: Browser Control (PinchTab)
description: 使用 PinchTab 控制浏览器自动化操作，包括导航、点击、输入、截图等
keywords: browser, automation, pinchtab, scrape, crawl, click, type, screenshot
---

# Browser Control (PinchTab)

使用 PinchTab 进行浏览器自动化操作。

## 前提

用户需要先在本地启动 PinchTab 服务：
```bash
pinchtab serve
```
默认服务地址：`http://localhost:9867`

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /navigate | 导航到 URL |
| GET | /snapshot?mode=readable | 获取可读快照 |
| GET | /snapshot?filter=interactive | 只获取可交互元素 |
| GET | /text | 获取页面文本 |
| POST | /action | 执行操作 |
| GET | /screenshot | 截图 |

## 操作示例

### 1. 导航
```bash
curl -X POST http://localhost:9867/navigate \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

### 2. 获取可交互元素
```bash
curl "http://localhost:9867/snapshot?filter=interactive"
```
返回 ref (如 e0, e1)，用于后续操作

### 3. 点击
```bash
curl -X POST http://localhost:9867/action \
  -H "Content-Type: application/json" \
  -d '{"kind":"click","ref":"e1"}'
```

### 4. 输入
```bash
curl -X POST http://localhost:9867/action \
  -H "Content-Type: application/json" \
  -d '{"kind":"type","ref":"e1","text":"hello"}'
```

### 5. 按键
```bash
curl -X POST http://localhost:9867/action \
  -H "Content-Type: application/json" \
  -d '{"kind":"press","key":"Enter"}'
```

## 使用流程

1. **导航** → 打开目标网页
2. **snapshot?filter=interactive** → 查看可点击的元素（获取 ref）
3. **action click/type** → 操作元素
4. **screenshot** → 查看结果

## 代码实现

```python
import httpx

client = httpx.Client(base_url="http://localhost:9867")

# 导航
client.post("/navigate", json={"url": "https://example.com"})

# 获取可交互元素
nodes = client.get("/snapshot?filter=interactive").json()["nodes"]
# [{'ref': 'e0', 'role': 'button', 'name': 'Submit'}]

# 点击
client.post("/action", json={"kind": "click", "ref": "e0"})

# 输入
client.post("/action", json={"kind": "type", "ref": "e1", "text": "hello"})

# 截图
img = client.get("/screenshot").content
```
