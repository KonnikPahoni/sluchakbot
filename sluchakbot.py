# coding=utf-8
import time

import telegram
from environs import Env
from telegram.error import NetworkError
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from file_parser import Parser
from access_logger import Logger
import os
import datetime

LOGGING_FILE = "var/access_log.txt"  # access log file
USERS_FILE = "var/users.txt"  # list of user IDs who interacted with the bot
START_PATH = "/main.txt"  # entry point for the /start command
TIMEOUT_TIME = 3600  # /broadcast command conversation timeout

BROADCAST_REQUESTED = 0  # Conversation handler return code
BROADCAST_CONFIRMED = 1  # Conversation handler return code
RECONNECT_INTERVAL = 5


class SluchakBot:
    access_logger = Logger(LOGGING_FILE)
    users = set()
    admins = set()
    broadcast_message = None

    def start(self):
        if not os.path.isfile(USERS_FILE):
            with open(USERS_FILE, "w") as users_file:
                users_file.write(datetime.datetime.now().isoformat() + " FILE CREATED")
        else:
            with open(USERS_FILE, "r") as users_file:
                self.users = set(map(lambda x: x.strip(), users_file.readlines()[1:]))

        self.admins = set(env.list("ADMIN_ID"))

        self.access_logger.write("POLLING STARTED")

        while True:
            try:
                self.updater.start_polling()
            except NetworkError as e:
                self.access_logger.write(
                    "Network error. Reconnecting in "
                    + str(RECONNECT_INTERVAL)
                    + " seconds"
                )
                time.sleep(RECONNECT_INTERVAL)
            except KeyboardInterrupt:
                self.access_logger.write("POLLING STOPPING")

    def __start_broadcast_command(self, update, context):
        if str(update.message.from_user.id) in self.admins:
            message_line = "START BROADCAST BY " + str(update.message.from_user)
            self.access_logger.write(message_line)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode="HTML",
                disable_web_page_preview=True,
                text="Паведамленьне атрымаюць "
                + str(len(self.users))
                + " карыстальнікаў. Калі ласка, дашліце мне тэкст паведамленьня.",
            )

        return BROADCAST_REQUESTED

    def __confirm_broadcast(self, update, context):
        self.broadcast_message = update.message.text

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="HTML",
            text="<b>Вось як будзе выглядаць вашае паведамленьне:</b>\n\n"
            + self.broadcast_message
            + "\n\n<b>Дашліце /confirm каб пацьвердзіць.</b>",
        )

        return BROADCAST_CONFIRMED

    def __broadcast_command(self, update, context):
        print(self.admins)
        if str(update.message.from_user.id) in self.admins:
            message_line = "BROADCAST " + self.broadcast_message
            self.access_logger.write(message_line)
            messages_sent = 0
            for user_id in self.users:
                try:
                    context.bot.send_message(
                        chat_id=user_id,
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                        text=self.broadcast_message,
                        reply_markup=telegram.InlineKeyboardMarkup(
                            [
                                [
                                    telegram.InlineKeyboardButton(
                                        text="Перайсці да размовы з СЛУЧАКом",
                                        callback_data=START_PATH,
                                    )
                                ]
                            ]
                        ),
                    )
                    messages_sent += 1
                except (telegram.error.Unauthorized, telegram.error.BadRequest) as e:
                    self.access_logger.write("BOT STOPPED BY USER " + user_id)

            context.bot.send_message(
                chat_id=update.message.from_user.id,
                text=str(messages_sent)
                + " паведамленняў даслана. "
                + str(len(self.users) - messages_sent)
                + " карыстальнікаў спынілі бота.",
            )
        return ConversationHandler.END

    def __start_command(self, update, context):
        message_line = "START " + str(update.message.from_user)
        self.access_logger.write(message_line)

        user_id = str(update.message.from_user.id)
        if user_id not in self.users:
            with open(USERS_FILE, "a") as users_file:
                users_file.write("\n" + user_id)
                self.users.add(user_id.strip())

        parser = Parser(START_PATH)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode="HTML",
            disable_web_page_preview=True,
            text=parser.get_text(),
            reply_markup=parser.get_markup(),
        )

    def __callback(self, update, context):
        message_line = (
            "CALLBACK "
            + str(update.callback_query.data)
            + " "
            + str(update.callback_query.from_user)
        )
        self.access_logger.write(message_line)
        parser = Parser(update.callback_query.data)
        callback_message = update.callback_query.message
        image_message = parser.get_image(as_media_photo=True)

        parser_file = parser.get_file()

        if not parser_file:
            if callback_message.reply_to_message:  # If previous photo exists
                if image_message:  # if new photo provided
                    context.bot.edit_message_media(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.reply_to_message.message_id,
                        media=image_message,
                    )

                    context.bot.edit_message_text(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.message_id,
                        text=parser.get_text(),
                        reply_markup=parser.get_markup(),
                        reply_to_message_id=callback_message.reply_to_message.message_id,
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )

                else:  # if new photo is not provided but previous photo exists
                    context.bot.delete_message(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.reply_to_message.message_id,
                    )

                    context.bot.send_message(
                        chat_id=callback_message.chat_id,
                        text=parser.get_text(),
                        reply_markup=parser.get_markup(),
                        disable_web_page_preview=True,
                        parse_mode="HTML",
                    )

                    context.bot.delete_message(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.message_id,
                    )

            elif image_message:
                new_image = context.bot.send_photo(
                    chat_id=update.effective_chat.id, photo=parser.get_image()
                )

                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    text=parser.get_text(),
                    reply_markup=parser.get_markup(),
                    reply_to_message_id=new_image.message_id,
                )

                context.bot.delete_message(
                    chat_id=callback_message.chat_id,
                    message_id=callback_message.message_id,
                )

            else:
                context.bot.send_message(
                    chat_id=callback_message.chat_id,
                    text=parser.get_text(),
                    reply_markup=parser.get_markup(),
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )

                context.bot.delete_message(
                    chat_id=callback_message.chat_id,
                    message_id=callback_message.message_id,
                )

        else:
            context.bot.send_document(
                chat_id=update.effective_chat.id, document=parser_file
            )
            context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id
            )

    @staticmethod
    def __cancel_command(update, context):
        return ConversationHandler.END

    def __init__(self, telegram_token_text):
        self.updater = Updater(token=telegram_token_text, use_context=True)

        start_handler = CommandHandler("start", self.__start_command)
        cancel_handler = CommandHandler("cancel", self.__cancel_command)
        broadcast_handler = ConversationHandler(
            entry_points=[CommandHandler("broadcast", self.__start_broadcast_command)],
            states={
                BROADCAST_REQUESTED: [
                    MessageHandler(Filters.all, self.__confirm_broadcast)
                ],
                BROADCAST_CONFIRMED: [
                    CommandHandler("confirm", self.__broadcast_command)
                ],
                ConversationHandler.TIMEOUT: [cancel_handler],
            },
            fallbacks=[cancel_handler],
            conversation_timeout=TIMEOUT_TIME,
        )
        button_handler = CallbackQueryHandler(self.__callback)

        self.updater.dispatcher.add_handler(start_handler)
        self.updater.dispatcher.add_handler(broadcast_handler)
        self.updater.dispatcher.add_handler(button_handler)
        self.updater.dispatcher.add_handler(cancel_handler)


if __name__ == "__main__":
    env = Env()
    env.read_env()
    TELEGRAM_TOKEN = str(os.environ["TELEGRAM_TOKEN"])

    sluchak_bot = SluchakBot(TELEGRAM_TOKEN)
    sluchak_bot.start()
