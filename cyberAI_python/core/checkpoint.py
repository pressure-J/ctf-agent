"""Checkpoint 文件存储(对齐 Go fileCheckPointStore): 每条 id 一个文件 (dir/id.ckpt)。"""
import os, json


class CheckpointStore:
    def __init__(self, base_dir: str = "data/checkpoints"):
        self.dir = os.path.abspath(base_dir)
        os.makedirs(self.dir, exist_ok=True)

    def _path(self, id_: str) -> str:
        id_ = str(id_).strip()
        if not id_ or ("/" in id_ or "\\" in id_):
            raise ValueError("invalid checkpoint id")
        return os.path.join(self.dir, id_ + ".ckpt")

    def save(self, id_: str, data: dict) -> bool:
        with open(self._path(id_), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return True

    def load(self, id_: str):
        p = self._path(id_)
        if not os.path.exists(p):
            return None, False
        with open(p, encoding="utf-8") as f:
            return json.load(f), True

    def list(self) -> list:
        return sorted(f[:-5] for f in os.listdir(self.dir) if f.endswith(".ckpt"))
