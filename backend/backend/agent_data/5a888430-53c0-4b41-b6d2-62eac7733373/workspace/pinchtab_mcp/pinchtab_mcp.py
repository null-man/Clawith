"""
PinchTab MCP Server - 浏览器自动化工具
包装 PinchTab 的 HTTP API 为 MCP 工具
"""

import os
import httpx
from typing import Optional

# 配置 - 用户本地 PinchTab
PINCHTAB_URL = os.getenv("PINCHTAB_URL", "http://localhost:9867")
PINCHTAB_TOKEN = os.getenv("PINCHTAB_TOKEN", "")


class PinchTabClient:
    """PinchTab HTTP API 客户端"""
    
    def __init__(self, base_url: str = PINCHTAB_URL, token: str = PINCHTAB_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.client = httpx.Client(timeout=30.0)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.base_url}{endpoint}"
        resp = self.client.request(method, url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        return resp.json()
    
    def health(self) -> dict:
        """健康检查"""
        return self._request("GET", "/health")
    
    def navigate(self, url: str) -> dict:
        """导航到指定 URL"""
        return self._request("POST", "/navigate", json={"url": url})
    
    def snapshot(self, mode: str = "readable") -> dict:
        """
        获取页面 accessibility tree
        mode: "readable" 或 "raw"
        """
        return self._request("GET", f"/snapshot?mode={mode}")
    
    def click(self, element_id: str) -> dict:
        """点击元素"""
        return self._request("POST", "/action", json={
            "action": "click",
            "element_id": element_id
        })
    
    def type(self, element_id: str, text: str) -> dict:
        """输入文本"""
        return self._request("POST", "/action", json={
            "action": "type",
            "element_id": element_id,
            "text": text
        })
    
    def press(self, key: str) -> dict:
        """按下键盘按键"""
        return self._request("POST", "/action", json={
            "action": "press",
            "key": key
        })
    
    def screenshot(self) -> bytes:
        """获取截图（返回 JPEG 二进制）"""
        url = f"{self.base_url}/screenshot"
        resp = self.client.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.content
    
    def find_element(self, selector: str, by: str = "text") -> dict:
        """
        查找元素
        by: "text" 或 "css" 或 "xpath"
        """
        return self._request("GET", f"/find?by={by}&selector={selector}")
    
    def text(self, element_id: Optional[str] = None) -> str:
        """获取元素或页面文本"""
        if element_id:
            return self._request("GET", f"/text?element_id={element_id}")
        return self._request("GET", "/text")
    
    def close(self):
        """关闭客户端"""
        self.client.close()


# 全局客户端实例
_client: Optional[PinchTabClient] = None


def get_client() -> PinchTabClient:
    global _client
    if _client is None:
        _client = PinchTabClient()
    return _client


# ============ MCP 工具函数 ============

def pinchtab_health() -> str:
    """检查 PinchTab 服务是否正常运行"""
    client = get_client()
    result = client.health()
    return f"PinchTab 服务状态: {result}"


def pinchtab_navigate(url: str) -> str:
    """导航浏览器到指定 URL
    
    Args:
        url: 目标网址 (例如: https://example.com)
    """
    client = get_client()
    result = client.navigate(url)
    return f"已导航到: {url}\n结果: {result}"


def pinchtab_snapshot(mode: str = "readable") -> str:
    """获取当前页面的 accessibility tree，用于理解页面结构
    
    Args:
        mode: "readable" (易读格式) 或 "raw" (原始格式)
    """
    client = get_client()
    result = client.snapshot(mode=mode)
    # 限制输出长度
    text = result.get("text", "")[:5000]
    return f"页面 Snapshot ({mode} 模式):\n\n{text}"


def pinchtab_click(element_id: str) -> str:
    """点击页面元素
    
    Args:
        element_id: 元素的 ID (从 snapshot 中获取)
    """
    client = get_client()
    result = client.click(element_id)
    return f"点击元素 {element_id}: {result}"


def pinchtab_type(element_id: str, text: str) -> str:
    """向输入框输入文本
    
    Args:
        element_id: 元素 ID
        text: 要输入的文本
    """
    client = get_client()
    result = client.type(element_id, text)
    return f"向元素 {element_id} 输入文本: {result}"


def pinchtab_press(key: str) -> str:
    """按下键盘按键
    
    Args:
        key: 按键名称 (例如: "Enter", "Escape", "ArrowDown")
    """
    client = get_client()
    result = client.press(key)
    return f"按下按键 {key}: {result}"


def pinchtab_find(selector: str, by: str = "text") -> str:
    """查找页面元素
    
    Args:
        selector: 选择器 (文本或 CSS 选择器)
        by: 查找方式 "text" (按文本) 或 "css" (按 CSS 选择器)
    """
    client = get_client()
    result = client.find_element(selector, by=by)
    return f"查找元素 (by={by}, selector={selector}):\n{result}"


def pinchtab_get_text(element_id: Optional[str] = None) -> str:
    """获取页面或元素的文本内容
    
    Args:
        element_id: 可选，元素 ID，不提供则获取整个页面文本
    """
    client = get_client()
    result = client.text(element_id)
    return f"页面文本:\n{result}"


# ============ MCP Server 注册 ============

MCP_TOOLS = [
    {
        "name": "pinchtab_health",
        "description": "检查 PinchTab 服务状态",
        "function": pinchtab_health
    },
    {
        "name": "pinchtab_navigate",
        "description": "导航浏览器到指定 URL",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "目标网址"}
            },
            "required": ["url"]
        },
        "function": pinchtab_navigate
    },
    {
        "name": "pinchtab_snapshot",
        "description": "获取页面 accessibility tree",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["readable", "raw"], "default": "readable"}
            }
        },
        "function": pinchtab_snapshot
    },
    {
        "name": "pinchtab_click",
        "description": "点击页面元素",
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_id": {"type": "string", "description": "元素 ID"}
            },
            "required": ["element_id"]
        },
        "function": pinchtab_click
    },
    {
        "name": "pinchtab_type",
        "description": "向输入框输入文本",
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_id": {"type": "string", "description": "元素 ID"},
                "text": {"type": "string", "description": "要输入的文本"}
            },
            "required": ["element_id", "text"]
        },
        "function": pinchtab_type
    },
    {
        "name": "pinchtab_press",
        "description": "按下键盘按键",
        "inputSchema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "按键名称"}
            },
            "required": ["key"]
        },
        "function": pinchtab_press
    },
    {
        "name": "pinchtab_find",
        "description": "查找页面元素",
        "inputSchema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "选择器"},
                "by": {"type": "string", "enum": ["text", "css"], "default": "text"}
            },
            "required": ["selector"]
        },
        "function": pinchtab_find
    },
    {
        "name": "pinchtab_get_text",
        "description": "获取页面或元素文本",
        "inputSchema": {
            "type": "object",
            "properties": {
                "element_id": {"type": "string", "description": "元素 ID（可选）"}
            }
        },
        "function": pinchtab_get_text
    }
]


if __name__ == "__main__":
    # 测试
    print("PinchTab MCP Server")
    print("=" * 40)
    print(f"连接地址: {PINCHTAB_URL}")
    
    try:
        client = get_client()
        health = client.health()
        print(f"✓ 服务连接成功: {health}")
    except Exception as e:
        print(f"✗ 服务连接失败: {e}")
        print("请确保 PinchTab 正在运行 (localhost:9867)")
