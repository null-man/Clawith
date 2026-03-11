"""
PinchTab Browser Control 实现
通过 HTTP API 控制本地浏览器
"""

import httpx
from typing import Optional
import os

# 默认配置
PINCHTAB_URL = os.getenv("PINCHTAB_URL", "http://localhost:9867")


class PinchTab:
    """PinchTab API 客户端"""
    
    def __init__(self, url: str = PINCHTAB_URL):
        self.url = url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
    
    def _get(self, path: str) -> dict:
        resp = self.client.get(f"{self.url}{path}")
        resp.raise_for_status()
        return resp.json()
    
    def _post(self, path: str, json: Optional[dict] = None) -> dict:
        resp = self.client.post(f"{self.url}{path}", json=json or {})
        resp.raise_for_status()
        return resp.json()
    
    def navigate(self, url: str) -> dict:
        """导航到 URL"""
        return self._post("/navigate", {"url": url})
    
    def snapshot(self, mode: str = "readable", filter_type: str = None) -> dict:
        """获取页面快照"""
        path = f"/snapshot?mode={mode}"
        if filter_type:
            path += f"&filter={filter_type}"
        return self._get(path)
    
    def click(self, ref: str) -> dict:
        """点击元素"""
        return self._post("/action", {"kind": "click", "ref": ref})
    
    def fill(self, ref: str, text: str) -> dict:
        """填写输入框"""
        return self._post("/action", {"kind": "fill", "ref": ref, "text": text})
    
    def press(self, ref: str, key: str) -> dict:
        """按键"""
        return self._post("/action", {"kind": "press", "ref": ref, "key": key})
    
    def hover(self, ref: str) -> dict:
        """悬停"""
        return self._post("/action", {"kind": "hover", "ref": ref})
    
    def focus(self, ref: str) -> dict:
        """聚焦"""
        return self._post("/action", {"kind": "focus", "ref": ref})
    
    def find(self, by: str, selector: str) -> dict:
        """查找元素"""
        return self._get(f"/find?by={by}&selector={selector}")
    
    def screenshot(self) -> bytes:
        """截图"""
        resp = self.client.get(f"{self.url}/screenshot")
        resp.raise_for_status()
        return resp.content
    
    def close(self):
        self.client.close()


# 全局实例
_browser: Optional[PinchTab] = None


def get_browser() -> PinchTab:
    global _browser
    if _browser is None:
        _browser = PinchTab()
    return _browser


# ============ 格式化输出 ============

def format_snapshot(data: dict) -> str:
    """格式化页面快照数据"""
    parts = []
    
    # URL
    if "url" in data:
        parts.append(f"🌐 URL: {data['url']}")
    
    # Title
    if "title" in data:
        parts.append(f"📑 标题: {data['title']}")
    
    # Mode
    if "mode" in data:
        parts.append(f"📊 模式: {data['mode']}")
    
    parts.append("")
    
    # Elements
    elements = data.get("elements", [])
    if elements:
        parts.append(f"🔗 可交互元素 ({len(elements)} 个):")
        parts.append("")
        
        for i, elem in enumerate(elements[:20], 1):  # 最多显示20个
            ref = elem.get("ref", "?")
            role = elem.get("role", "?")
            text = elem.get("text", "")
            tag = elem.get("tag", "")
            
            # 简化显示
            text_preview = text[:50] + "..." if len(text) > 50 else text
            text_str = f' "{text_preview}"' if text_preview else ""
            
            parts.append(f"  {i}. [{ref}] {role}: <{tag}>{text_str}")
        
        if len(elements) > 20:
            parts.append(f"  ... 还有 {len(elements) - 20} 个元素")
    
    # 完整文本
    if "text" in data:
        text = data["text"]
        if text:
            parts.append("")
            parts.append("📝 页面文本:")
            parts.append("─" * 40)
            # 限制长度
            if len(text) > 3000:
                text = text[:3000] + "\n... (truncated)"
            parts.append(text)
    
    return "\n".join(parts)


def format_elements(data: dict) -> str:
    """格式化元素列表"""
    elements = data.get("elements", [])
    if not elements:
        return "未找到元素"
    
    parts = [f"🔍 找到 {len(elements)} 个元素:", ""]
    
    for i, elem in enumerate(elements, 1):
        ref = elem.get("ref", "?")
        role = elem.get("role", "?")
        text = elem.get("text", "")[:40]
        tag = elem.get("tag", "")
        
        parts.append(f"{i}. [{ref}] {role}: <{tag}> \"{text}\"")
    
    return "\n".join(parts)


# ============ 对话式工具函数 ============

def navigate(url: str) -> str:
    """导航到 URL"""
    b = get_browser()
    result = b.navigate(url)
    title = result.get("title", "")
    return f"✅ 已打开: {url}\n📑 页面标题: {title}"


def snapshot(mode: str = "readable", interactive_only: bool = False) -> str:
    """获取页面快照"""
    b = get_browser()
    filter_type = "interactive" if interactive_only else None
    result = b.snapshot(mode, filter_type)
    return format_snapshot(result)


def click(ref: str) -> str:
    """点击元素"""
    b = get_browser()
    result = b.click(ref)
    return f"👆 已点击: [{ref}]"


def fill(ref: str, text: str) -> str:
    """填写输入框"""
    b = get_browser()
    result = b.fill(ref, text)
    return f"⌨️ 已填写 [{ref}]: \"{text}\""


def press(ref: str, key: str) -> str:
    """按键"""
    b = get_browser()
    result = b.press(ref, key)
    return f"⌨️ 已按键: {key}"


def hover(ref: str) -> str:
    """悬停"""
    b = get_browser()
    result = b.hover(ref)
    return f"🖱️ 已悬停: [{ref}]"


def focus(ref: str) -> str:
    """聚焦"""
    b = get_browser()
    result = b.focus(ref)
    return f"🎯 已聚焦: [{ref}]"


def find(by: str, selector: str) -> str:
    """查找元素"""
    b = get_browser()
    result = b.find(by, selector)
    return format_elements(result)


# ============ 对话式入口 ============

async def handle_browser_command(command: str, **kwargs) -> str:
    """
    处理浏览器控制命令
    对话式入口，供 Agent 调用
    """
    handlers = {
        "navigate": lambda: navigate(kwargs.get("url", "")),
        "snapshot": lambda: snapshot(
            kwargs.get("mode", "readable"),
            kwargs.get("interactive_only", False)
        ),
        "click": lambda: click(kwargs.get("ref", "")),
        "fill": lambda: fill(kwargs.get("ref", ""), kwargs.get("text", "")),
        "press": lambda: press(kwargs.get("ref", ""), kwargs.get("key", "")),
        "hover": lambda: hover(kwargs.get("ref", "")),
        "focus": lambda: focus(kwargs.get("ref", "")),
        "find": lambda: find(kwargs.get("by", "text"), kwargs.get("selector", "")),
    }
    
    handler = handlers.get(command)
    if handler:
        return handler()
    return f"未知命令: {command}"


if __name__ == "__main__":
    # 测试
    b = PinchTab()
    print("PinchTab 连接测试...")
    print(navigate("https://www.baidu.com"))
    print(snapshot(interactive_only=True))
