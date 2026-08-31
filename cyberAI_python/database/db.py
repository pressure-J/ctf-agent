"""
数据库连接和操作 - 完整版
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import uuid

from .models import Base, User, Conversation, Message, Agent, ToolExecution, Workflow, AuditLog


class Database:
    """数据库管理类"""
    
    def __init__(self, database_url: str = "sqlite:///data/cyberstrike.db"):
        import os
        os.makedirs("data", exist_ok=True)
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def init(self):
        """初始化数据库"""
        Base.metadata.create_all(bind=self.engine)
    
    # ========== 用户操作 ==========
    
    def create_user(self, username: str, password_hash: str, email: str = None) -> str:
        """创建用户"""
        
        user_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            user = User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                email=email
            )
            session.add(user)
        
        return user_id
    
    def get_user(self, username: str) -> Optional[Dict]:
        """获取用户"""
        
        with self.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            
            if user:
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active
                }
        
        return None
    
    def get_user_with_password(self, username: str) -> Optional[Dict]:
        """认证专用: 返回含 password_hash 的用户(仅供登录比对, 常规查询不暴露)"""
        with self.get_session() as session:
            u = session.query(User).filter(User.username == username).first()
            if u:
                return {"id": u.id, "username": u.username,
                        "password_hash": u.password_hash, "role": u.role}
        return None

    # ========== 对话操作 ==========
    
    def create_conversation(self, user_id: str, title: str = None) -> str:
        """创建对话"""
        
        conversation_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                title=title or f"对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            session.add(conversation)
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """获取对话"""
        
        with self.get_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                messages = [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "tool_calls": msg.tool_calls,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in conversation.messages
                ]
                
                return {
                    "id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat(),
                    "messages": messages
                }
        
        return None
    
    def list_conversations(self, user_id: str) -> List[Dict]:
        """列出用户对话"""
        
        with self.get_session() as session:
            conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).all()
            
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
    
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Dict = None
    ):
        """保存消息"""
        
        message_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata_=metadata or {}
            )
            session.add(message)
            
            # 更新对话时间
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.updated_at = datetime.utcnow()
    
    # ========== Agent操作 ==========
    
    def create_agent(self, config: Dict) -> str:
        """创建Agent"""
        
        agent_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            agent = Agent(
                id=agent_id,
                name=config["name"],
                description=config.get("description"),
                mode=config.get("mode", "single"),
                system_prompt=config.get("system_prompt"),
                model=config.get("model", "deepseek-chat"),
                config=config.get("config", {})
            )
            session.add(agent)
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """获取Agent"""
        
        with self.get_session() as session:
            agent = session.query(Agent).filter(Agent.id == agent_id).first()
            
            if agent:
                return {
                    "id": agent.id,
                    "name": agent.name,
                    "description": agent.description,
                    "mode": agent.mode,
                    "system_prompt": agent.system_prompt,
                    "model": agent.model,
                    "config": agent.config
                }
        
        return None
    
    def list_agents(self) -> List[Dict]:
        """列出所有Agent"""
        
        with self.get_session() as session:
            agents = session.query(Agent).filter(Agent.is_active == True).all()
            
            return [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "description": agent.description,
                    "mode": agent.mode
                }
                for agent in agents
            ]
    
    # ========== 工具执行记录 ==========
    
    def save_tool_execution(
        self,
        agent_id: str,
        conversation_id: str,
        tool_name: str,
        arguments: Dict,
        result: str,
        success: bool,
        execution_time: int
    ):
        """保存工具执行记录"""
        
        execution_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            execution = ToolExecution(
                id=execution_id,
                agent_id=agent_id,
                conversation_id=conversation_id,
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                success=success,
                execution_time=execution_time
            )
            session.add(execution)
    
    def count_tool_executions(self) -> int:
        """统计工具执行次数"""
        
        with self.get_session() as session:
            return session.query(ToolExecution).count()
    
    # ========== 工作流操作 ==========
    
    def create_workflow(self, definition: Dict) -> str:
        """创建工作流"""
        
        workflow_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            workflow = Workflow(
                id=workflow_id,
                name=definition["name"],
                description=definition.get("description"),
                definition=definition
            )
            session.add(workflow)
        
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """获取工作流"""
        
        with self.get_session() as session:
            workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
            
            if workflow:
                return {
                    "id": workflow.id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "definition": workflow.definition
                }
        
        return None
    
    def list_workflows(self) -> List[Dict]:
        """列出工作流"""
        
        with self.get_session() as session:
            workflows = session.query(Workflow).filter(Workflow.is_active == True).all()
            
            return [
                {
                    "id": wf.id,
                    "name": wf.name,
                    "description": wf.description
                }
                for wf in workflows
            ]
    
    # ========== 审计日志 ==========
    
    def save_audit_log(
        self,
        user_id: str,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        details: Dict = None,
        ip_address: str = None
    ):
        """保存审计日志"""
        
        log_id = str(uuid.uuid4())
        
        with self.get_session() as session:
            log = AuditLog(
                id=log_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address
            )
            session.add(log)
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        
        with self.get_session() as session:
            logs = session.query(AuditLog).order_by(
                AuditLog.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
    
    # ========== 统计 ==========
    
    def count_conversations(self) -> int:
        """统计对话数"""
        
        with self.get_session() as session:
            return session.query(Conversation).count()

    def count_users(self) -> int:
        """统计用户数"""

        with self.get_session() as session:
            return session.query(User).count()

    def count_workflows(self) -> int:
        """统计工作流数"""

        with self.get_session() as session:
            return session.query(Workflow).count()
    
    def count_messages(self) -> int:
        """统计消息数"""
        
        with self.get_session() as session:
            return session.query(Message).count()
