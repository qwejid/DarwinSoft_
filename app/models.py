from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from .database import Base

class User(Base):
    
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    tasks: Mapped[list['Task']] = relationship('Task', back_populates='owner', cascade='all, delete-orphan')

class Task(Base):

    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    owner: Mapped[User] = relationship('User', back_populates='tasks')
    permissions: Mapped[list['TaskPermission']] = relationship('TaskPermission', back_populates='task', cascade='all, delete-orphan')

class TaskPermission(Base):

    __table_args__ = (
        UniqueConstraint('task_id', 'user_id'),
    )

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    can_read: Mapped[bool] = mapped_column(Boolean, default=False)
    can_update: Mapped[bool] = mapped_column(Boolean, default=False)

    task: Mapped[Task] = relationship('Task', back_populates='permissions')
    user: Mapped[User] = relationship('User')