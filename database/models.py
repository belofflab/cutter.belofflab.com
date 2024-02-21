import datetime
from gino import Gino
from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    String,
    DateTime,
    Boolean,
    Table,
)

db = Gino()


class User(db.Model):
    __tablename__ = "users"

    id: int = Column(BigInteger, primary_key=True)
    username: str = Column(String(255), nullable=True)
    full_name: str = Column(String(255))
    created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.now)


class Shortcut(db.Model):
    __tablename__ = "shortcuts"

    id: int = Column(BigInteger, primary_key=True)
    code: str = Column(String(255), unique=True)
    target_link: str = Column(String(255), nullable=False)
    click_count: int = Column(BigInteger, default=0)
    unique_click_count: int = Column(BigInteger, default=0)
    created_at: datetime.datetime = Column(DateTime, default=datetime.datetime.now)
    is_active: bool = Column(Boolean, default=True)

class UserShortcut(db.Model):
    __tablename__ = "users_shortcuts"
    id = Column(BigInteger(), primary_key=True)
    user_id = Column(BigInteger(), db.ForeignKey("users.id"), nullable=False)
    shortcut_id = Column(BigInteger(), db.ForeignKey("shortcuts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(), default=datetime.datetime.now)



class ForwardingClient(db.Model):
    __tablename__ = "forwarding_clients"

    id: int = Column(BigInteger, primary_key=True)
    ip_address: str = Column(String(45), unique=True)
    timestamp: datetime.datetime = Column(DateTime, default=datetime.datetime.now)


class ShortcutClient(db.Model):
    __tablename__ = "shortcuts_clients"
    id = Column(BigInteger(), primary_key=True)
    shortcut_id = Column(BigInteger(), db.ForeignKey("shortcuts.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(BigInteger(), ForeignKey("forwarding_clients.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(), default=datetime.datetime.now)
