# settings.py
# обработчик внешних файлов config.cfg и lastmod.log в папке с программой

import configparser
import datetime


# Пришлось создать класс для списка
class SetForList:
    # last_upd_time = datetime.datetime.now() - datetime.timedelta(days=1)
    # Add a list to store processed files
    processed_files = []
    last_processed_files = []


config = configparser.ConfigParser()
config.read('config.cfg')

# Указываем пути к папкам, в которых будем отслеживать появление новых файлов
folder1_path = config['FOLDERS']['Folder1_Path']
print("Папка отслеживания 1:", folder1_path)
folder2_path = config['FOLDERS']['Folder2_Path']
print("Папка отслеживания 2:", folder2_path)

# Указываем путь к папке, куда нужно распаковывать файлы
extract_path = config['FOLDERS']['Extract_Path']
print("Путь распаковки:", extract_path)

# Указываем путь к файлу lastmod.log
lastmod_file = config['FILES']['Lastmod_Path']

# Указываем путь к файлу lastUpdSoftTime.log
lastupd_file = config['FILES']['LastUpd_Path']

# Указываем путь к файлу ProcessedFiles.log
processed_file = config['FILES']['Processed_files']

with open(processed_file) as prfile:
    SetForList.processed_files = prfile.read().splitlines()

# Указываем путь расположения программы WinRAR
winrar = config['PROGRAMS']['WinRAR_Path']
print("Путь к WinRAR:", winrar)

# Указываем путь к внешней программе и аргументы её запуска
command_to_run = config['PROGRAMS']['Command_to_run']
print("Команда выполнения внешней программы:", command_to_run)

# окно пуска внешней программы:
start_time = config['TIME']['Start_time']
end_time = config['TIME']['End_time']
start_time = datetime.datetime.strptime(start_time, '%H:%M:%S').time()
end_time = datetime.datetime.strptime(end_time, '%H:%M:%S').time()

# Берём из конфига интервал сканирования
intervalt = config['TIME']['Interval_time']
interval = int(intervalt)
print('Установленный интервал обхода папок:', interval)

# Читаем дату последней модификации архивов из файла lastmod.log
with open(lastmod_file, 'r') as f:
    last_update_time = f.read().strip()

    # преобразуем строку даты последнего изменения архивов в объект datetime.time
    last_update_time = datetime.datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S.%f')

# читаем дату последнего запуска внешней программы из файла
with open(lastupd_file, 'r') as f2:
    lastUpdSoftTime = f2.read().strip()
    # преобразуем строку даты последнего запуска внешней программы в объект datetime.time
    lastUpdSoftTime = datetime.datetime.strptime(lastUpdSoftTime, '%Y-%m-%d %H:%M:%S.%f')

# выдаём из этого модуля переменные:
# folder(X)_path - папки слежения
# extract_path - папка распаковки
# last_update_time - дата последнего изменения архивов в формате datetime
# lastUpdSoftTime - дата и время последнего запуска внешней программы
# winrar - архиватор
# command_to_run - команда выполнения внешней программы
# interval - интервал сканирования папок
# start_time - параметры окна пуска внешней программы
# end_time - параметры окна пуска внешней программы
