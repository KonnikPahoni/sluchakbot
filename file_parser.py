import telegram


class Parser:

    def __init__(self, path):
        self.__image = None
        self.__text = ''
        self.__markup = []
        self.__file = None

        if_file_path = path[:5]

        if if_file_path != 'file=':
            file = open('files' + path, "r", encoding='utf-8')
            while True:
                line = file.readline()
                if not line:
                    break
                if line.strip() == 'Image=':
                    self.__image = file.readline().strip()
                    file.readline()
                elif line.strip() == 'Text=':
                    while True:
                        textline = file.readline()
                        if not textline or textline.strip() == '=EndText':
                            break
                        self.__text += textline
                elif line.strip() == 'Buttons=':
                    while True:
                        button_type = file.readline().strip()
                        if not button_type or button_type == '=EndButtons':
                            break
                        goto = file.readline().strip()
                        text = file.readline().strip()
                        if button_type == 'link':
                            self.__markup.append([telegram.InlineKeyboardButton(text=text, url=goto)])
                        elif button_type == 'local':
                            self.__markup.append([telegram.InlineKeyboardButton(text=text, callback_data=goto)])
                elif line.strip() == 'DoubleButtons=':
                    while True:
                        button_row = []
                        button_type = file.readline().strip()
                        if not button_type or button_type == '=EndDoubleButtons':
                            break
                        goto = file.readline().strip()
                        text = file.readline().strip()
                        if button_type == 'link':
                            button_row.append(telegram.InlineKeyboardButton(text=text, url=goto))
                        elif button_type == 'local':
                            button_row.append(telegram.InlineKeyboardButton(text=text, callback_data=goto))
                        button_type = file.readline().strip()
                        goto = file.readline().strip()
                        text = file.readline().strip()
                        if button_type == 'link':
                            button_row.append(telegram.InlineKeyboardButton(text=text, url=goto))
                        elif button_type == 'local':
                            button_row.append(telegram.InlineKeyboardButton(text=text, callback_data=goto))
                        self.__markup.append(button_row)
            file.close()
        else:
            self.__file = if_file_path

    def get_text(self):
        return self.__text

    def get_markup(self):
        return telegram.InlineKeyboardMarkup(self.__markup)

    def get_image(self, as_media_photo=False):
        if not self.__image:
            return None
        if not as_media_photo:
            return open('files' + self.__image, "rb")
        else:
            return telegram.InputMediaPhoto(media=open('files' + self.__image, "rb"))
