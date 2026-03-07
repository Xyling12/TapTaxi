#!/usr/bin/env python3
"""
TapTaxi Device Lock — Keygen Bot
Генерирует код активации по Android Device ID

Команда: /gencode <device_id>
Формат кода: 8 символов HEX (пример: A3F8C2D1)
"""

import hmac
import hashlib
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === НАСТРОЙКИ ===
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"
ADMIN_CHAT_IDS = {376060133}  # только ты можешь генерировать коды
SECRET = "TapTaxi_DevLock_2026_SECRET_KEY_v1"  # ⚠️ не менять между версиями APK!
# =================


def generate_code(device_id: str) -> str:
    """Генерирует постоянный 8-символьный код для данного device_id"""
    device_id = device_id.strip().lower()
    sig = hmac.new(SECRET.encode(), device_id.encode(), hashlib.sha256).hexdigest()
    return sig[:8].upper()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *TapTaxi Device Lock Bot*\n\n"
        "Команды:\n"
        "`/gencode <device_id>` — сгенерировать код активации\n\n"
        "Device ID водитель видит на экране активации приложения.",
        parse_mode="Markdown"
    )


async def cmd_gencode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Проверяем доступ
    if chat_id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("❌ Доступ запрещён.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Укажи Device ID:\n`/gencode abc123def456`",
            parse_mode="Markdown"
        )
        return

    device_id = context.args[0]
    code = generate_code(device_id)

    await update.message.reply_text(
        f"✅ *Код активации*\n\n"
        f"Device ID: `{device_id}`\n"
        f"Код: `{code}`\n\n"
        f"Действует на этом устройстве постоянно.",
        parse_mode="Markdown"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("gencode", cmd_gencode))
    print("✅ Keygen bot запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
