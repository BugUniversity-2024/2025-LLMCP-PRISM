"""
数据库模型 - 会话和版本
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    versions = relationship("Version", back_populates="session", cascade="all, delete-orphan", order_by="Version.version_number")

    def __repr__(self):
        return f"<Session(id={self.id})>"


class Version(Base):
    """版本表"""
    __tablename__ = "versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    parent_version_id = Column(String(36), ForeignKey("versions.id", ondelete="SET NULL"), nullable=True)

    # 用户输入
    user_input = Column(Text, nullable=True)
    user_feedback = Column(Text, nullable=True)

    # Prompt 数据（存储为 JSON）
    schema = Column(JSON, nullable=False)
    prompt = Column(Text, nullable=False)
    diff = Column(JSON, nullable=True)

    # 图片数据
    image_url = Column(String(500), nullable=False)
    image_path = Column(String(500), nullable=False)

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    session = relationship("Session", back_populates="versions")
    parent_version = relationship("Version", remote_side=[id], backref="children")

    # 索引
    __table_args__ = (
        Index("idx_session_versions", "session_id", "version_number"),
        Index("idx_parent_version", "parent_version_id"),
        Index("idx_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Version(id={self.id}, session={self.session_id}, v{self.version_number})>"

