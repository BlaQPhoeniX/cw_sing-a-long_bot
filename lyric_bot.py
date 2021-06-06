#!/usr/bin/env python3

import logging
import os
import re

from collections import defaultdict

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Welcome to {context.bot.name}'
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Just send me the lyrics and I will reply with the formatted text.')


def markup_lyrics(update: Update, context: CallbackContext) -> None:
    """Take user submitted lyrics and mark it up."""
    lyrics = update.message.text
    hashed_lyrics = re.sub(r"(\w+)", r"#\1", lyrics)
    lyrics = re.sub(r"[^a-zA-Z\s']", "", lyrics)
    words = list(set(lyrics.lower().split()))
    words.sort()
    missing = defaultdict(list)
    rune_count = defaultdict(int)
    for word in words:
        missing[word[0]].append(word)
        for c in word:
            rune_count[c] += 1

    word_list = str()
    rune_list = str()

    sorted_rune_count = sorted(rune_count.items(), key=lambda x: x[1], reverse=True)

    for i in sorted_rune_count:
        rune_list += f"<code>{i[0].upper()}</code>     {i[1]}\n"

    for k,v in missing.items():
        word_string = " - ".join(v)
        word_list += f"<code>{k.upper()}</code>     {word_string}\n"

    formatted_text = f"{hashed_lyrics}\n\n<b>MISSING WORDS</b>\n{word_list}\n\n<b>RUNE DEMAND</b>\n{rune_list}"

    update.message.reply_text(formatted_text, parse_mode="HTML")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ['TOKEN'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, markup_lyrics))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
