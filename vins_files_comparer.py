
from validance_checker import check_validance


def find_different_lines(file1_path, file2_path):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        lines1 = file1.readlines()
        lines2 = file2.readlines()

        # Создаем множества из строк в файлах
        set1 = set(lines1)
        set2 = set(lines2)

        # Ищем различающиеся строки в каждом из множеств
        diff1 = set1 - set2
        diff2 = set2 - set1

        # Выводим информацию о различающихся строках
        if len(diff1) == 0 and len(diff2) == 0:
            print("Файлы совпадают.")
        else:
            if len(diff1) > 0:
                print(f"В файле {file1_path} есть следующие различающиеся строки:")
                for line in diff1:
                    print(line.rstrip())
                with open(f'{file1_path}_SUB_{file2_path}', 'w', encoding='utf-8') as f:
                    f.writelines(diff1)
            if len(diff2) > 0:
                print(f"В файле {file2_path} есть следующие различающиеся строки:")
                for line in diff2:
                    print(line.rstrip())


#  Функция выявления винов, которые есть в первом файле, но отсутствуют во втором.
#  Опциональна. В main по умолчанию не используется.
def compare_vins_files(file_1, file_2):

    file_1_valid = f'{file_1}_valid'
    file_2_valid = f'{file_2}_valid'
    check_validance(file_1, file_1_valid)
    check_validance(file_2, file_2_valid)

    find_different_lines(file_1_valid, file_2_valid)


compare_vins_files('vins_dtp_2', 'vins_dtp')
