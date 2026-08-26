
"""审计日志 - 仓库层封装 SQLAlchemy 查询, 供 service/路由调用
TODO: 把 database/db.py 中的增删改查逻辑拆到各仓库, 避免 db.py 臃肿
"""
from typing import Dict, Optional, List
import logging
logger = logging.getLogger(__name__)

class AuditRepoRepo:
    def __init__(self, db):
        self.db = db
