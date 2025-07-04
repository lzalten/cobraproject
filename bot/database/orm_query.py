import datetime
import json

from sqlalchemy import delete, update, select, func, bindparam
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession


from database.models import User, Deposit, Withdraw, Bonus, SingleGame, MinesGame


async def orm_add_object(obj, session: AsyncSession):
    session.add(obj)
    await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def get_game_by_message_id(session: AsyncSession, message_id: int):
    query = select(SingleGame).where(SingleGame.message_id == message_id, SingleGame.status == "CREATED")
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_transaction_sums(session: AsyncSession, user_id: int) -> dict:
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    month_ago = now - datetime.timedelta(days=30)

    # Запрос для сумм пополнений пользователя
    deposits_total = await session.execute(select(func.sum(Deposit.amount)).where(Deposit.user_id == user_id))
    deposits_week = await session.execute(select(func.sum(Deposit.amount)).where(Deposit.user_id == user_id, Deposit.date >= week_ago))
    deposits_month = await session.execute(select(func.sum(Deposit.amount)).where(Deposit.user_id == user_id, Deposit.date >= month_ago))

    # Запрос для сумм выводов пользователя
    withdrawals_total = await session.execute(select(func.sum(Withdraw.amount)).where(Withdraw.user_id == user_id))
    withdrawals_week = await session.execute(select(func.sum(Withdraw.amount)).where(Withdraw.user_id == user_id, Withdraw.date >= week_ago))
    withdrawals_month = await session.execute(select(func.sum(Withdraw.amount)).where(Withdraw.user_id == user_id, Withdraw.date >= month_ago))

    return {
        "deposits": {
            "total": deposits_total.scalar() or 0,
            "week": deposits_week.scalar() or 0,
            "month": deposits_month.scalar() or 0
        },
        "withdrawals": {
            "total": withdrawals_total.scalar() or 0,
            "week": withdrawals_week.scalar() or 0,
            "month": withdrawals_month.scalar() or 0
        }
    }


async def orm_get_bonus(session: AsyncSession, bonus_id: int):
    query = select(Bonus).where(Bonus.id == bonus_id)
    result = await session.execute(query)
    return result.scalar()


async def get_used_bonuses_for_user(session: AsyncSession, user_id: int):
    query = select(Bonus.id).where(Bonus.users_ids.op('@>')(bindparam('user_ids', value=json.dumps([user_id]), type_=JSONB)))
    result = await session.execute(query, {'user_ids': [user_id]})
    return result.scalars().all()

async def get_bonus1_deposit(session: AsyncSession, user_id: int):
    query = select(Deposit.id).where(Deposit.user_id == user_id, Deposit.amount >= 500)
    result = await session.execute(query)
    return result.scalar()


async def get_bonus2_withdraw(session: AsyncSession, user_id: int):
    query = select(Withdraw.id).where(Withdraw.user_id == user_id, Withdraw.amount >= 1000)
    result = await session.execute(query)
    return result.scalar()

async def create_bonus_objects_from_0_to_7(session: AsyncSession):
    for i in range(8):
        # Проверяем, существует ли объект с таким ID
        result = await session.execute(select(Bonus).where(Bonus.id == i))
        existing_bonus = result.scalars().first()

        if not existing_bonus:
            # Если не существует, создаем
            new_bonus = Bonus(id=i, amount=10, users_ids=[])  # users_ids по умолчанию []
            session.add(new_bonus)

    await session.commit()


async def get_games_for_user(session: AsyncSession, user_id: int):
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    month_ago = now - datetime.timedelta(days=30)

    games_total = await session.execute(select(func.count(SingleGame.id)).where(SingleGame.user_id == user_id))
    games_day = await session.execute(select(func.count(SingleGame.id)).where(SingleGame.user_id == user_id, SingleGame.date >= now))
    games_week = await session.execute(select(func.count(SingleGame.id)).where(SingleGame.user_id == user_id, SingleGame.date >= week_ago))
    games_month = await session.execute(select(func.count(SingleGame.id)).where(SingleGame.user_id == user_id, SingleGame.date >= month_ago))

    return {
        "total": games_total.scalar() or 0,
        "day": games_day.scalar() or 0,
        "week": games_week.scalar() or 0,
        "month": games_month.scalar() or 0
    }


async def get_earned_money_from_referral(session: AsyncSession, user_id: int) -> float:
    """Возвращает сумму денег, заработанных пользователем с рефералов."""

    # Находим всех пользователей, у которых данный user_id является реферальным
    stmt = select(User.id).where(User.referrer_id == user_id)
    result = await session.execute(stmt)
    referral_ids = [row[0] for row in result.fetchall()]

    if not referral_ids:
        return 0.0  # Если рефералов нет, возвращаем 0

    # Суммируем все депозиты этих пользователей, которые помечены как оплаченные рефоводу
    stmt = select(func.coalesce(func.sum(Deposit.paid_to_referrer), 0)).where(
        Deposit.user_id.in_(referral_ids)
    )
    result = await session.execute(stmt)
    total_earned = result.scalar() or 0.0

    return total_earned


async def get_valid_referrals_count(session: AsyncSession, user_id: int) -> int:
    """Подсчитывает количество рефералов, которые сделали ставок на 300₽."""

    result = await session.execute(
        select(User.user_id)
        .where(User.referrer_id == user_id)
        .where(
            select(func.sum(SingleGame.amount))
            .where(SingleGame.user_id == User.user_id)
            .having(func.sum(SingleGame.amount) >= 300)
            .exists()
        )
    )
    return len(result.scalars().all())


# MINES

async def orm_get_mines_game_by_id(session: AsyncSession, mines_id: int):
    query = select(MinesGame).where(MinesGame.id == mines_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_active_mines_game_for_user(session: AsyncSession, user_id: int):
    query = select(MinesGame).where(MinesGame.user_id == user_id, MinesGame.status == 'CREATED')
    result = await session.execute(query)
    return result.scalar()

# async def orm_get_paymentorder(session: AsyncSession, user_id: int):
#     query = select(PaymentOrder).where(PaymentOrder.user_id == user_id).where(PaymentOrder.status == 'created')
#     result = await session.execute(query)
#     return result.scalar()
#
#
# async def orm_get_game(session: AsyncSession, message_id: int, user_id: int):
#     query = select(Game).where(Game.message_id == message_id).where(Game.user_id == user_id)
#     result = await session.execute(query)
#     return result.scalar()
