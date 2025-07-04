from aiogram.fsm.state import StatesGroup, State


class OrderPayment(StatesGroup):
    price = State()
    waiting_for_text = State()

    async def clear(self) -> None:
        await self.set_state(state=None)
        await self.set_data({})
