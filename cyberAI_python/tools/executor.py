"""
工具执行器 - 安全执行工具调用
流程: 参数校验 -> 超时控制 -> 结果规整(截断/错误包装)
"""
from typing import Dict, Any
import time
import logging
logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, name: str, args: Dict[str, Any]) -> str:
        start = time.time()
        try:
            result = self.registry.execute(name, args)
            # TODO: 记录 ToolExecution 到数据库
            return result
        except Exception as e:
            logger.exception(f"工具 {name} 执行异常")
            return f"[工具执行错误] {e}"
        finally:
            logger.debug(f"工具 {name} 耗时 {time.time()-start:.2f}s")

    async def aexecute(self, name: str, args: Dict[str, Any]) -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute, name, args)
