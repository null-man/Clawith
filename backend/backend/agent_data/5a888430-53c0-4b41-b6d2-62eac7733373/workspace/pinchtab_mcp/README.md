# PinchTab MCP Server

一个简单的 MCP server，包装 PinchTab 浏览器自动化工具的 HTTP API。

## 功能

- `navigate` - 导航到指定 URL
- `snapshot` - 获取当前页面的 accessibility tree
- `click` - 点击元素
- `type` - 输入文本
- `screenshot` - 获取截图
- `find_element` - 查找元素

## 配置

需要设置环境变量：
- `PINCHTAB_URL` - PinchTab 服务地址（默认 http://localhost:8080）
- `PINCHTAB_TOKEN` - 认证 token（可选）

## 运行

```bash
# 安装依赖
pip install fastmcp httpx

# 启动服务
python pinchtab_mcp.py
```

## 测试

服务启动后，可以通过 MCP 协议调用各工具。
