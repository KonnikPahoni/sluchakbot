import os
import datetime


class Logger:

    def __init__(self, path, run_silent=False):
        self.__filename = path
        self.__run_silent = run_silent

        if not os.path.isfile(self.__filename):
            with open(self.__filename, "w") as logging_file:
                logging_file.write('')

        self.write('BOT LAUNCHED')

    def __print(self, line):
        if not self.__run_silent:
            print(line)

    def write(self, line):
        formatted_line = datetime.datetime.now().isoformat() + ' ' + line
        self.__print(formatted_line)
        with open(self.__filename, "a", encoding="utf-8") as logging_file:
            logging_file.write(formatted_line + '\n')
