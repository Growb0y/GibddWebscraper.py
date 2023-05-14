import os
import pathlib
import requests
import datetime
import threading
from time import sleep

from captcha_reader import pass_captcha


def parse_site(input_vins_file_, output_dir_, checkType_):
    """
    функция парсинга разделов "history" и "dtp" сайта ГИБДД
    :param input_vins_file_: string - название входного файла с винами
    :param output_dir_: string - название папки, куда записывется выходной файл
    :param checkType_: string - вид проверки (history/dtp)
    :return: None (функция записывает спаршенные данные в файл)
    """

    url = 'https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/' + checkType_
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }

    # Парсим, пока для всех винов не будет получен удовлетворительный ответ
    while True:

        def post_(vin_, i_):
            print(f"posting {i_}...")
            datas_ = {'vin': vin_, 'checkType': checkType_, 'captchaWord': captcha["captchaWord"], 'captchaToken': captcha["captchaToken"]}
            resp = requests.post(data=datas_, url=url, headers=headers)
            print(f"\nResponse №{i_} info:")
            print("Sent datas: ", datas_)
            print(f"Response code: {resp.status_code}")
            if resp.status_code == 500:
                print("Internal Server Error")
                return None
            resp_json = resp.json()
            print(f"Response.json: {resp_json}")
            return resp_json

        # Проходим капчу
        while True:
            captcha = pass_captcha()
            resp_json = post_('XUS2327BKN0000561', 1)  # Тестовый номер
            if resp_json is None:
                pass
            elif 'message' in resp_json:
                if resp_json['message'] == 'Проверка CAPTCHA не была пройдена из-за неверного введенного значения.':
                    print("Неверно введена CAPTCHA.")
                elif resp_json['message'] == 'Срок действия кода CAPTCHA устарел, попробуйте снова.':
                    print("Срок действия кода CAPTCHA устарел.")
                else:
                    is_captcha_valid = True
                    break
            else:
                is_captcha_valid = True
                break

        vins_file = input_vins_file_

        dir_ = f"{output_dir_}/{checkType_}"

        pathlib.Path(dir_).mkdir(parents=True, exist_ok=True)  # создаём папку, если она не существует

        # Создаём копию вин-файла для работы
        vins_file_copy = f'{dir_}/vins_copy.txt'
        if not os.path.exists(vins_file_copy):
            with open(vins_file, 'r') as f1:
                # Открываем новый файл для записи
                with open(vins_file_copy, 'w') as f2:
                    # Читаем содержимое исходного файла
                    data = f1.read()
                    # Записываем содержимое в новый файл
                    f2.write(data)

        # dt = datetime.datetime.now()
        # print('==================================================')
        # print('ДАТА И ВРЕМЯ ЗАПРОСА:  ', dt)
        # print('==================================================')

        def post_data(vin_, i_, lock_file_writing_):

            nonlocal captcha
            nonlocal is_captcha_valid

            resp_json = post_(vin_, i_)
            if resp_json is None:
                return
            if 'message' in resp_json:
                if resp_json['message'] == "Срок действия кода CAPTCHA устарел, попробуйте снова.":
                    print("Срок действия кода CAPTCHA устарел.")
                    is_captcha_valid = False
                    return
                elif resp_json['message'] == 'Проверка CAPTCHA не была пройдена из-за неверного введенного значения.':
                    print("Неверно введена CAPTCHA.")
                    is_captcha_valid = False
                    return

            with lock_file_writing_:
                lines[i_-1] = '#' + vin_ + '\n'  # Ставим # перед проверенным вином
                file_data.write(f"{i_} ::: {vin_} ::: {resp_json}\n")  # Записываем результат в выходной файл

        lock_file_writing = threading.Lock()
        data_file_path = f"{dir_}/data.txt"
        file_data = open(data_file_path, 'a', encoding='utf-8')
        with open(vins_file_copy, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        threads = []
        x = {}

        # Создаём потоки для распараллеливания ожидания ответов сервера
        for i, l in enumerate(lines, 1):
            if l.startswith('#'):
                continue
            if not is_captcha_valid:
                break
            vin = l[:-1]  # l[:-1] - слайс без символа \n
            x[i] = threading.Thread(target=post_data, args=(vin, i, lock_file_writing))
            threads.append(x[i])
            x[i].start()
            sleep(0.25)  # избегаем превышения частоты запросов на сервер

        # Ожидаем завершения всех потоков, чтобы глобальная функция не завершилась раньше нужного времени
        for thread in threads:
            thread.join()

        # Перезаписываем рабочий вин-файл данные с дополнительной информацией о проверенных винах
        with open(vins_file_copy, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        file_data.close()

        # Проверка того, проверены ли все вины
        def is_file_parsed(vins_file_copy):
            with open(vins_file_copy, 'r') as file:
                lines = file.readlines()
                for line in lines[:-1]:
                    if not line.startswith('#'):
                        return False
            return True

        if is_file_parsed(vins_file_copy):
            return
