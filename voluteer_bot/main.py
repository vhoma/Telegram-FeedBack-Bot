#!/usr/bin/env python
# pylint: disable=unused-argument


import logging
import sys
import os
import json

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


DEFAULT_CFG_FILE = "config.json"
CONFIG = None   # placeholder

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_msg = CONFIG["start_message"]
    if str(update.effective_chat.type).endswith("group"):
        group_id = update.effective_chat.id
        reply_msg += f"\n\n{group_id=}"
    await update.message.reply_html(
        reply_msg
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(CONFIG["help_message"])


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    # await update.message.reply_text(update.message.text)
    try:
        await update.message.forward(CONFIG['group_id'])
    except Exception as ex:
        logger.exception("Ignoring exception during forward......")


def read_json_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"Something went wrong when loading file: {file_name}")


def main() -> None:
    # STEP 1. Read json config
    config_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CFG_FILE
    global CONFIG
    CONFIG = read_json_file(config_file)

    # STEP 2. Initialize
    application = Application.builder().token(token=CONFIG['token']).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - forward the message on Telegram
    application.add_handler(MessageHandler(filters.ALL, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
