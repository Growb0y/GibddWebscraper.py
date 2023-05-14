
from resources.lists import russian_to_english


def check_validance(input_vins_file_, valid_vins_file_):
    """
    функция проверки винов на валидность
    :param input_vins_file_: string - название входного файла с винами
    :param valid_vins_file__: string - название файла, куда записываются валидные вины
    :return: None (функция записывает спаршенные данные в файл)
    """

    def replace_russian_letters(string_):
        string = string_
        for ch in russian_to_english:
            string = string.replace(ch, russian_to_english[ch])
        if not string.isascii():
            print(string, 'Удалено. Незаменяемые неанглийские символы.')
            return None
        if string_ != string:
            print(string, 'Исправлено. Заменяемые русские символы.')
        else:
            print(string)
        return string

    with open(input_vins_file_, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    desired_length = len('XUS2327BKN0000561')
    new_lines = []
    print('CheckLog:')
    for line in lines:
        line = line[:-1]
        if line == '':
            continue
        if len(line) == desired_length:
            line = replace_russian_letters(line)
            if line is not None:
                new_lines.append(line)
        else:
            print(line, 'Удалено. Невалидная длина.')

    with open(valid_vins_file_, 'w', encoding='utf-8') as file:
        file.write('\n'.join(new_lines))
        file.write('\n')
