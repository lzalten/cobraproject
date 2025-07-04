import datetime
from typing import List

from sqlalchemy import DateTime, func, ForeignKey, Column, Integer, String, Float, JSON, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    ...

class User(Base):
    __tablename__ = "casino_user"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    referrer_id = Column(BigInteger, nullable=True)
    balance = Column(Float, nullable=False, default=0.0)
    reg_date = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)

class Deposit(Base):
    __tablename__ = 'casino_deposit'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('casino_user.user_id'), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default='created')
    paid_to_referrer: Mapped[int] = mapped_column(nullable=True)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

class Withdraw(Base):
    __tablename__ = 'casino_withdraw'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('casino_user.user_id'), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default='created')
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

class Bonus(Base):
    __tablename__ = 'casino_bonus'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    users_ids: Mapped[List[int]] = mapped_column(JSONB, default=[], nullable=False)

class SingleGame(Base):
    __tablename__ = 'casino_singlegame'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('casino_user.user_id'), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    game_type: Mapped[str] = mapped_column(nullable=False)
    game_value: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default='CREATED')
    message_id: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

class MinesGame(SingleGame):
    __tablename__ = 'casino_minesgame'

    id: Mapped[int] = mapped_column(ForeignKey('casino_singlegame.id'), primary_key=True)  # Исправляем ForeignKey
    current_prize: Mapped[float] = mapped_column(nullable=False)
    mines_array: Mapped[List[int]] = mapped_column(JSONB, default=[], nullable=False)
    clicked_array: Mapped[List[int]] = mapped_column(JSONB, default=[], nullable=False)

    __mapper_args__ = {
        "inherit_condition": id == SingleGame.id
    }