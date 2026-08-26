"""
数据模型 - 完整版
使用SQLAlchemy ORM
"""

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关系
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    """对话表"""
    
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default={})
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """消息表"""
    
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, default=[])
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")


class Agent(Base):
    """Agent配置表"""
    
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    mode = Column(String(20), default="single")  # single, supervisor, plan_execute
    system_prompt = Column(Text)
    model = Column(String(50), default="deepseek-chat")
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class ToolExecution(Base):
    """工具执行记录表"""
    
    __tablename__ = "tool_executions"
    
    id = Column(String(36), primary_key=True)
    agent_id = Column(String(36))
    conversation_id = Column(String(36))
    tool_name = Column(String(100), nullable=False)
    arguments = Column(JSON, default={})
    result = Column(Text)
    success = Column(Boolean, default=True)
    execution_time = Column(Integer)  # 毫秒
    created_at = Column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    """工作流表"""
    
    __tablename__ = "workflows"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    definition = Column(JSON, nullable=False)  # 工作流定义
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class AuditLog(Base):
    """审计日志表"""
    
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36))
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    details = Column(JSON, default={})
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
