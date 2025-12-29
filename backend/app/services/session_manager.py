"""
Session Manager - 会话和版本管理服务
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import desc
from pathlib import Path
from app.models import Session, Version


class SessionManager:
    """会话管理器"""

    def __init__(self, db: SQLSession):
        self.db = db

    def create_session(self) -> Session:
        """创建新会话"""
        session = Session(id=str(uuid4()))
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话（支持字符串类型的 ID）"""
        return self.db.query(Session).filter(Session.id == str(session_id)).first()

    def create_version(
        self,
        session_id: str,
        schema: Dict[str, Any],
        prompt: str,
        image_url: str,
        image_path: str,
        user_input: Optional[str] = None,
        user_feedback: Optional[str] = None,
        diff: Optional[Dict[str, Any]] = None,
        parent_version_id: Optional[str] = None
    ) -> Version:
        """
        创建新版本

        Args:
            session_id: 会话 ID
            schema: Prompt Schema
            prompt: 自然语言 Prompt
            image_url: 图片 URL
            image_path: 本地路径
            user_input: 用户输入（首次生成）
            user_feedback: 用户反馈（迭代优化）
            diff: Prompt Diff（迭代优化）
            parent_version_id: 父版本 ID

        Returns:
            Version 对象
        """
        # 计算版本号（当前会话的最大版本号 + 1）
        max_version = (
            self.db.query(Version)
            .filter(Version.session_id == session_id)
            .order_by(desc(Version.version_number))
            .first()
        )
        version_number = (max_version.version_number + 1) if max_version else 1

        # 创建版本
        version = Version(
            id=str(uuid4()),
            session_id=str(session_id),
            version_number=version_number,
            parent_version_id=str(parent_version_id) if parent_version_id else None,
            user_input=user_input,
            user_feedback=user_feedback,
            schema=schema,
            prompt=prompt,
            diff=diff,
            image_url=image_url,
            image_path=image_path
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)

        # 更新 Session 的 updated_at
        session = self.get_session(session_id)
        if session:
            self.db.commit()

        return version

    def get_version(
        self,
        session_id: str,
        version_number: int
    ) -> Optional[Version]:
        """获取指定版本"""
        return (
            self.db.query(Version)
            .filter(
                Version.session_id == str(session_id),
                Version.version_number == version_number
            )
            .first()
        )

    def get_all_versions(self, session_id: str) -> List[Version]:
        """获取会话的所有版本（按版本号排序）"""
        return (
            self.db.query(Version)
            .filter(Version.session_id == str(session_id))
            .order_by(Version.version_number)
            .all()
        )

    def get_version_tree(self, session_id: str) -> Dict[str, Any]:
        """
        构建版本树结构

        Returns:
            {
                "version_number": 1,
                "image_url": "...",
                "children": [
                    {"version_number": 2, "children": [...]},
                    {"version_number": 4, "children": []}
                ]
            }
        """
        versions = self.get_all_versions(session_id)
        if not versions:
            return {}

        # 构建树
        def build_tree(version: Version) -> Dict[str, Any]:
            node = {
                "id": str(version.id),
                "version_number": version.version_number,
                "user_input": version.user_input,
                "user_feedback": version.user_feedback,
                "image_url": version.image_url,
                "created_at": version.created_at.isoformat(),
                "children": []
            }

            # 查找子节点
            for v in versions:
                if v.parent_version_id == version.id:
                    node["children"].append(build_tree(v))

            return node

        # 查找根节点（parent_version_id 为 None）
        root = next((v for v in versions if v.parent_version_id is None), None)
        if not root:
            return {}

        return build_tree(root)

    def get_all_sessions(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[Session]:
        """获取所有项目列表（按更新时间倒序）"""
        return (
            self.db.query(Session)
            .order_by(desc(Session.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_sessions(self) -> int:
        """统计项目总数"""
        return self.db.query(Session).count()

    def update_session(
        self,
        session_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Session:
        """更新项目元数据"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError("项目不存在")

        if name is not None:
            session.name = name
        if description is not None:
            session.description = description

        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: str) -> bool:
        """删除项目（级联删除版本和图片文件）"""
        session = self.get_session(session_id)
        if not session:
            return False

        # 删除所有关联图片文件
        for version in session.versions:
            try:
                if version.image_path:
                    image_file = Path(version.image_path)
                    if image_file.exists():
                        image_file.unlink()
            except Exception as e:
                print(f"删除图片失败: {e}")

        # 删除会话（级联删除版本记录）
        self.db.delete(session)
        self.db.commit()
        return True

