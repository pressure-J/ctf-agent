"""
AI 通道配置管理(对齐 Go settings/AI 通道): 多通道 + 默认 + CRUD + 测试连接。
配置 JSON 持久化到 data/ai_channels.json(非数据库表, 属全局运维配置)。
字段对齐 Go: name / provider / base_url / api_key / model / max_context / max_output / is_default。
"""
import os, json, time, uuid
from pathlib import Path

# 首次默认通道(api_key 留空=回退 .env; 用户在管理页可填)
DEFAULT_CHANNELS = [{
    "id": "deepseek", "name": "DeepSeek", "provider": "openai",
    "base_url": "https://api.deepseek.com", "api_key": "",
    "model": "deepseek-chat", "max_context": 120000, "max_output": 32768,
    "is_default": True, "enabled": True,
    "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
}]


class AiChannelManager:
    def __init__(self, path: str = "data/ai_channels.json"):
        self.path = Path(path)
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._save(DEFAULT_CHANNELS)

    def _load(self) -> list:
        if not self.path.exists():
            return list(DEFAULT_CHANNELS)
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return list(DEFAULT_CHANNELS)

    def _save(self, channels):
        self.path.write_text(json.dumps(channels, ensure_ascii=False, indent=2), encoding="utf-8")

    def list(self) -> list:
        """返回通道列表(api_key 脱敏)"""
        return [{**c, "api_key": (c["api_key"][:4] + "****") if c.get("api_key") else ""} for c in self._load()]

    def get(self, ch_id) -> dict:
        for c in self._load():
            if c["id"] == ch_id:
                return c
        return None

    def default(self) -> dict:
        chs = self._load()
        for c in chs:
            if c.get("is_default"):
                return c
        return chs[0] if chs else None

    def add(self, cfg: dict) -> dict:
        chs = self._load()
        ch = {"id": cfg.get("id") or "ch_" + uuid.uuid4().hex[:8],
              "name": cfg.get("name", ""), "provider": cfg.get("provider", "openai"),
              "base_url": cfg.get("base_url", ""), "api_key": cfg.get("api_key", ""),
              "model": cfg.get("model", ""), "max_context": cfg.get("max_context", 120000),
              "max_output": cfg.get("max_output", 32768),
              "is_default": cfg.get("is_default", False), "enabled": cfg.get("enabled", True),
              "created": cfg.get("created", time.strftime("%Y-%m-%dT%H:%M:%S"))}
        chs.append(ch); self._save(chs); return ch

    def update(self, ch_id, cfg: dict) -> dict:
        chs = self._load()
        for c in chs:
            if c["id"] == ch_id:
                for k, v in cfg.items():
                    if k not in ("id", "created"):
                        c[k] = v
                self._save(chs); return c
        raise KeyError(ch_id)

    def delete(self, ch_id):
        chs = [c for c in self._load() if c["id"] != ch_id]
        self._save(chs)

    def set_default(self, ch_id):
        chs = self._load()
        for c in chs:
            c["is_default"] = (c["id"] == ch_id)
        self._save(chs)

    def test_connection(self, cfg: dict) -> dict:
        """探活: 用给定通道配置调 models.list(不生成, 省钱)。api_key 空则回退 .env"""
        from openai import OpenAI
        try:
            cli = OpenAI(api_key=cfg.get("api_key") or os.getenv("DEEPSEEK_API_KEY"),
                         base_url=cfg.get("base_url") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
            cli.models.list()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
