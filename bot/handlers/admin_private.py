from aiogram import Router
from filters.chat_types import IsAdmin, IsAdminCallback

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdminCallback())