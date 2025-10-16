import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.exceptions import TelegramBadRequest

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_USERNAME = "@neverstopIovinggg"
REACTION_EMOJI = "❤️"
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
@dp.message(F.chat.type.in_({"supergroup", "group"}))
async def check_subscription(message: types.Message):
    """Проверяет подписку пользователя при каждом комментарии."""

    # 🔹 Игнорируем сообщения от самого канала (post от имени канала)
    if message.sender_chat:
        return

    # 🔹 Игнорируем сообщения от самого бота
    if message.from_user.id == (await bot.me()).id:
        return

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    try:
        # Проверяем подписку пользователя
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        status = member.status

        if status in ("member", "administrator", "creator"):
            # ✅ Подписан — ставим реакцию
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[types.ReactionTypeEmoji(emoji=REACTION_EMOJI)]
            )
        else:
            raise TelegramBadRequest(method="getChatMember", message="User not subscribed")

    except TelegramBadRequest:
        # 🚫 Не подписан — пишем предупреждение
        warn_msg = await bot.send_message(
            chat_id=message.chat.id,
            reply_to_message_id=message.message_id,
            text=(
                f"@{username}, добро пожаловать! 👋\n"
                f"Мы заметили, что вы не подписаны на канал {CHANNEL_USERNAME} "
                "и не можем пропустить ваш комментарий.\n"
                "Пожалуйста, подпишитесь, чтобы участвовать в обсуждении ❤️"
            ),
        )

        # Удаляем комментарий
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        # Удаляем предупреждение через 15 секунд
        await asyncio.sleep(15)
        await bot.delete_message(chat_id=message.chat.id, message_id=warn_msg.message_id)

    except Exception as e:
        print(f"⚠️ Ошибка: {type(e).__name__} — {e}")


async def main():
    print("🤖 Бот запущен и слушает чат комментариев...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Бот остановлен вручную.")
