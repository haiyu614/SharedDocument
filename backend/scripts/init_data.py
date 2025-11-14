"""初始化基础数据：创建默认角色"""
from __future__ import annotations

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.role import Role


def init_roles():
    """初始化默认角色"""
    db = SessionLocal()
    try:
        roles = [
            Role(name="admin", description="管理员，拥有所有权限"),
            Role(name="editor", description="编辑者，可以创建和编辑文档"),
            Role(name="viewer", description="查看者，只能查看文档"),
        ]
        for role in roles:
            existing = db.query(Role).filter(Role.name == role.name).first()
            if not existing:
                db.add(role)
                print(f"✅ 创建角色: {role.name}")
            else:
                print(f"⏭️  角色已存在: {role.name}")
        db.commit()
        print("\n✅ 角色初始化完成")
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_roles()

