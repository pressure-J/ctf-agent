"""上下文预算控制(对齐 Go internal/multiagent/context_budget)。
能力: 溢出错误检测 / 历史压缩(超预算) / 工具输出截断(marker)。
"""
OVERFLOW_MARKERS = [
    "context length", "context_length", "maximum context", "max context",
    "context window", "context overflow", "too many tokens", "token limit",
    "tokens exceed", "exceeds the context", "input is too long",
    "prompt is too long", "request too large", "tokens per minute",
]
TOOL_TRUNC_MARKER = "\n\n...[tool output truncated; full text persisted]...\n\n"


def is_context_overflow_error(err) -> bool:
    """API 拒绝 "上下文超长" 的识别(对齐 isEinoContextOverflowError)"""
    msg = str(err).lower()
    return any(m in msg for m in OVERFLOW_MARKERS)


def estimate_tokens(text) -> int:
    """粗略 token 估算: 中文≈1字/token, 英文≈4字符/token(够用,不精确)"""
    text = str(text)
    cjk = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    return cjk + int((len(text) - cjk) / 4) + 1


def messages_tokens(messages) -> int:
    return sum(estimate_tokens(m.get("content", "")) for m in messages)


def tool_output_truncate(content: str, max_bytes: int = 1200) -> str:
    """截断工具输出并加 marker(对齐 truncateBytesWithMarker)。默认比 Go 小(80? 中), 避免撑爆"""
    if max_bytes <= 0 or len(content) <= max_bytes:
        return content
    budget = max_bytes - len(TOOL_TRUNC_MARKER)
    return (content[:budget] if budget > 0 else "") + TOOL_TRUNC_MARKER


def compress_history(messages, max_tokens: int, keep_recent: int = 6):
    """超预算 -> 压缩: 保留 system + 最近 keep_recent 条, 早期历史换成摘要占位。
    对齐 Go eino summarization 中间件的"历史压缩保留上下文"思想。"""
    if messages_tokens(messages) <= max_tokens:
        return messages
    if len(messages) <= keep_recent + 1:
        return messages                       # 太少, 无可压缩
    head = messages[:1] if messages and messages[0].get("role") == "system" else []
    tail = messages[len(head):]
    return head + [{"role": "system",
                    "content": "(早期对话已压缩, 仅保留最新上下文)"}] + tail[-keep_recent:]
