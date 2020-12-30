# coding=utf-8

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from file_parser import Parser
from access_logger import Logger

LOGGING_FILE = 'files/access_log.txt'
START_PATH = '/main.txt'


class SluchakBot:
    access_logger = Logger(LOGGING_FILE)

    def start(self):
        self.updater.start_polling()
        self.access_logger.write('POLLING STARTED.')

    def __start_command(self, update, context):
        message_line = 'START ' + str(update.message.from_user)
        self.access_logger.write(message_line)

        parser = Parser(START_PATH)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode='HTML',
            disable_web_page_preview=True,
            text=parser.get_text(),
            reply_markup=parser.get_markup()
        )

    def __callback(self, update, context):
        message_line = 'CALLBACK ' + str(update.callback_query.data) + ' ' + str(update.callback_query.from_user)
        self.access_logger.write(message_line)
        parser = Parser(update.callback_query.data)
        callback_message = update.callback_query.message
        image_message = parser.get_image(as_media_photo=True)

        parser_file = parser.get_file()

        if not parser_file:

            if callback_message.reply_to_message:  # If previous photo exists

                if image_message:  # if new photo provided

                    context.bot.edit_message_media(chat_id=callback_message.chat_id,
                                                   message_id=callback_message.reply_to_message.message_id,
                                                   media=image_message)

                    context.bot.edit_message_text(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.message_id,
                        text=parser.get_text(),
                        reply_markup=parser.get_markup(),
                        reply_to_message_id=callback_message.reply_to_message.message_id,
                        disable_web_page_preview=True,
                        parse_mode='HTML')

                else:  # if new photo is not provided but previous photo exists

                    context.bot.delete_message(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.reply_to_message.message_id
                    )

                    context.bot.send_message(
                        chat_id=callback_message.chat_id,
                        text=parser.get_text(),
                        reply_markup=parser.get_markup(),
                        disable_web_page_preview=True,
                        parse_mode='HTML')

                    context.bot.delete_message(
                        chat_id=callback_message.chat_id,
                        message_id=callback_message.message_id
                    )

            elif image_message:

                new_image = context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=parser.get_image()
                )

                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    text=parser.get_text(),
                    reply_markup=parser.get_markup(),
                    reply_to_message_id=new_image.message_id)

                context.bot.delete_message(
                    chat_id=callback_message.chat_id,
                    message_id=callback_message.message_id
                )

            else:
                context.bot.send_message(
                    chat_id=callback_message.chat_id,
                    text=parser.get_text(),
                    reply_markup=parser.get_markup(),
                    disable_web_page_preview=True,
                    parse_mode='HTML')

                context.bot.delete_message(chat_id=callback_message.chat_id,
                                           message_id=callback_message.message_id
                                           )

        else:
            context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=parser_file)
            context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id
            )

    def __init__(self, telegram_token_text):
        self.updater = Updater(token=telegram_token_text, use_context=True)
        start_handler = CommandHandler('start', self.__start_command)
        self.updater.dispatcher.add_handler(start_handler)
        button_handler = CallbackQueryHandler(self.__callback)
        self.updater.dispatcher.add_handler(button_handler)


if __name__ == "__main__":
    with open('telegram_token') as telegram_token_file:
        telegram_token = telegram_token_file.readline()
    sluchak_bot = SluchakBot(telegram_token)
    sluchak_bot.start()
