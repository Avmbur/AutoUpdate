# отслеживание изменений, разархивация, перезапись lastmod-файла, запуск внешней если были новые архивы
import win32event
import win32api
import winerror
import sys
import settings
import os
import datetime
import time
import subprocess
import logging


# сначала защита от запуска нескольких копий
# Define a name for the mutex
mutex_name = "MyAppMutex"

# Create a named mutex
mutex = win32event.CreateMutex(None, False, mutex_name)

# Check if the mutex already exists
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    print("Другая копия of the program is already running.")
    # Release the mutex and exit the program
    win32api.CloseHandle(mutex)
    sys.exit()

# configure the logging module
# configure the root logger with a FileHandler and a StreamHandler
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logfile.log', mode='a'),
        logging.StreamHandler()
    ])


# функция распаковки архива из папки1
def unpack_file1(rar_file):
    # Формируем путь к файлу и проверяем его существование
    rar_file_path = os.path.join(settings.folder1_path, rar_file)
    if not os.path.exists(rar_file_path):
        logging.warning(f"Файл {rar_file_path} не найден")
        return

    # Wait for the file to finish being written
    file_size = os.path.getsize(rar_file_path)
    while True:
        time.sleep(3)
        new_file_size = os.path.getsize(rar_file_path)
        if new_file_size == file_size:
            break
        file_size = new_file_size

    # Проверяем, не был ли файл уже обработан
    if rar_file not in settings.SetForList.processed_files:
        # Формируем команду для распаковки архива с помощью WinRAR
        command = f'{settings.winrar} x -o+ -ep1 "{os.path.join(settings.folder1_path, rar_file)}" ' \
                  f'"{settings.extract_path}"'
        # Выполняем команду в отдельном процессе
        subprocess.Popen(command, shell=True).wait()
        print(f"Распаковка файла {rar_file}")
        # добавляем обработанный файл в список
        settings.SetForList.processed_files.append(rar_file)
        # пишем в лог о распаковке файла
        logging.info(f"Распаковка файла из папки 1: {rar_file}")


def unpack_file2(rar_file):
    rar_file_path = os.path.join(settings.folder2_path, rar_file)
    if not os.path.exists(rar_file_path):
        logging.warning(f"Файл {rar_file_path} не найден")
        return

    file_size = os.path.getsize(rar_file_path)
    while True:
        time.sleep(3)
        new_file_size = os.path.getsize(rar_file_path)
        if new_file_size == file_size:
            break
        file_size = new_file_size

    if rar_file not in settings.SetForList.processed_files:
        command = f'{settings.winrar} x -o+ -ep1 "{os.path.join(settings.folder2_path, rar_file)}" ' \
                  f'"{settings.extract_path}"'
        subprocess.Popen(command, shell=True).wait()
        print(f"Распаковка файла {rar_file}")
        settings.SetForList.processed_files.append(rar_file)
        logging.info(f"Распаковка файла из папки 2: {rar_file}")


while True:
    # Получаем список файлов в папках
    files1 = os.listdir(settings.folder1_path)
    files2 = os.listdir(settings.folder2_path)

    # Отбираем только файлы с расширением .rar
    rar_files1 = [f for f in files1 if f.endswith(".rar")]
    rar_files2 = [f for f in files2 if f.endswith(".rar")]

    # Проверяем, есть ли архивы, что-бы программа не завершилась преждевременно.
    if not rar_files1 and not rar_files2:
        print("Архивов в одной или обеих папках нет.")
        time.sleep(5)
        continue

    # Отбираем только новые архивы и сверяем со списком обработанных
    new_rar_files1 = [f for f in rar_files1 if datetime.datetime.fromtimestamp(
        os.path.getmtime(os.path.join(settings.folder1_path, f))) >
                      settings.last_update_time and f not in settings.SetForList.processed_files]

    new_rar_files2 = [f for f in rar_files2 if datetime.datetime.fromtimestamp(
        os.path.getmtime(os.path.join(settings.folder2_path, f))) >
                      settings.last_update_time and f not in settings.SetForList.processed_files]

    # Если есть новые архивы в папке 1, то распаковываем их
    if new_rar_files1:
        for rar_file in new_rar_files1:
            unpack_file1(rar_file)

    # Если есть новые архивы в папке 2, то распаковываем их
    if new_rar_files2:
        for rar_file in new_rar_files2:
            unpack_file2(rar_file)

    # сохраняем список обработанных архивов в файле ProcessedFiles.log
    new_processed_files = "\n".join(settings.SetForList.processed_files)
    if new_processed_files != settings.SetForList.last_processed_files:
        with open(settings.processed_file, "w") as prfile:
            prfile.write(new_processed_files)
            settings.SetForList.last_processed_files = new_processed_files

    # Обновляем значение даты последнего изменения файлов
    last_archive_time = max(
        [datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(settings.folder1_path, f))) for f in
         rar_files1] + [
            datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(settings.folder2_path, f))) for f in
            rar_files2])
    print('Время последнего обновления архивов:', last_archive_time)

    # если дата последнего обновления архивов отличается, записываем новое значение в файл
    # сначала прочитаем, что записано в файле
    with open(settings.lastmod_file, "r") as infiletime:
        infile_last_update_time = infiletime.read().strip()
        infile_last_update_time = datetime.datetime.strptime(infile_last_update_time, '%Y-%m-%d %H:%M:%S.%f')
        if last_archive_time > infile_last_update_time:
            # преобразуем значение datetime в строку и записываем в файл
            last_update_time_str = last_archive_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            with open(settings.lastmod_file, "w") as filetime:
                filetime.write(last_update_time_str)

            print('Файл lastmod.log изменён:', last_update_time_str)
            # пишем в лог о распаковке файла
            logging.info(f"'Файл lastmod.log изменён:', {last_update_time_str}")
            time.sleep(1)  # подождём, пусть файл запишется

    # окно пуска проверяем
    # get the current time
    now = datetime.datetime.now().time()
    print('Окно пуска внешней программы:', settings.start_time, '-', settings.end_time)
    # check if the current time is within the time window
    if settings.start_time <= now <= settings.end_time:
        # если дата последнего изменения архивов больше даты последнего запуска внешней
        # программы из файла LastUpdSoftTime.log, то запускаем внешнюю программу.
        if last_archive_time > settings.lastUpdSoftTime:
            print("Запущена внешняя программа в:", datetime.datetime.now())
            logging.info(f"'Запущена внешняя программа в:', {datetime.datetime.now()}")
            subprocess.Popen(settings.command_to_run, shell=True).wait()
            print("Внешняя программа завершила работу в:", datetime.datetime.now())
            logging.info(f"'Внешняя программа завершила работу в:', {datetime.datetime.now()}")

            # update lastUpdSoftTime with current time
            settings.lastUpdSoftTime = datetime.datetime.now()

            # записываем время последнего запуска внешней программы во внешний файл, предв преоб в строку
            # lastUpdSoftTime = settings.lastUpdSoftTime
            lastUpdSoftTime_str = settings.lastUpdSoftTime.strftime('%Y-%m-%d %H:%M:%S.%f')
            with open(settings.lastupd_file, "w") as fileupdtime:
                fileupdtime.write(lastUpdSoftTime_str)
                time.sleep(1)
            print('Время последнего запуска внешней программы изменено:', datetime.datetime.now())
            logging.info(f"'Время последнего запуска внешней программы изменено:', {datetime.datetime.now()}")

    else:
        print("Время последнего запуска внешней программы:", settings.lastUpdSoftTime)
        print("Новых архивов для распаковки нет. Ожидаем. \nВремя:", datetime.datetime.now())
        # Ждём интервал перед следующей проверкой
        time.sleep(settings.interval)

# Release the mutex
win32api.CloseHandle(mutex)
