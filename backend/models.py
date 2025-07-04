import datetime
from typing import List

from sqlalchemy import ForeignKey, func, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "casino_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)  # Изменяем на BigInteger
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)  # Изменяем на BigInteger
    balance: Mapped[float] = mapped_column(nullable=False, default=0.0)
    reg_date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, balance={self.balance})>"

class Deposit(Base):
    __tablename__ = 'casino_deposit'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('casino_user.user_id'), nullable=False)  # ForeignKey на BigInteger
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default='created')
    paid_to_referrer: Mapped[int] = mapped_column(BigInteger, nullable=True)  # Изменяем на BigInteger
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

    def __repr__(self):
        return f"<Deposit(id={self.id}, user_id={self.user_id}, amount={self.amount})>"

class Withdraw(Base):
    __tablename__ = 'casino_withdraw'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('casino_user.user_id'), nullable=False)  # ForeignKey на BigInteger
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default='created')
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

    def __repr__(self):
        return f"<Withdraw(id={self.id}, user_id={self.user_id}, amount={self.amount})>"

class Bonus(Base):
    __tablename__ = 'casino_bonus'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    users_ids: Mapped[List[int]] = mapped_column(JSONB, default=[], nullable=False)

    def __repr__(self):
        return f"<Bonus(id={self.id}, amount={self.amount})>"

class SingleGame(Base):
    __tablename__ = 'casino_singlegame'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('casino_user.user_id'), nullable=False)  # ForeignKey на BigInteger
    amount: Mapped[float] = mapped_column(nullable=False)
    game_type: Mapped[str] = mapped_column(nullable=False)
    game_value: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default='CREATED')
    message_id: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, default=func.now())

    def __repr__(self):
        return f"<SingleGame(id={self.id}, game_type={self.game_type}, status={self.status})>"

class MinesGame(SingleGame):
    __tablename__ = 'casino_minesgame'

    id: Mapped[int] = mapped_column(ForeignKey('casino_singlegame.id'), primary_key=True)
    current_prize: Mapped[float] = mapped_column(nullable=False)
    mines_array: Mapped[List[int]] = mapped_column(JSONB, default=[], nullable=False)
    clicked_array: Mapped[List[int]] = mapped_column(JSONB, default=[], nullable=False)

    __mapper_args__ = {
        "inherit_condition": id == SingleGame.id
    }

    def __repr__(self):
        return f"<MinesGame(id={self.id}, current_prize={self.current_prize})>"