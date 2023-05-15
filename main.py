import argparse
from validance_checker import check_validance
from site_parser import parse_site
from txt_to_parquet import convert_txt_to_prq
from parquet_to_excel import convert_prq_to_xlsx


root_dir = '.'

if __name__ == '__main__':

    # Аргументы для запуска программы из командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('vins_file', type=str, help='Файл с винами')
    parser.add_argument('required_types', type=str, help='Типы (history/dtp/all)')
    parser.add_argument('directory', type=str, help='Создаваемая папка с данными')
    parser.add_argument('--dont_parse_site', type=bool, help='Нужно ли парсить сайт', default=False)
    args = parser.parse_args()

    vins_file = args.vins_file
    required_types = args.required_types
    if required_types == 'all':
        required_types = ["history", "dtp"]
    iteration = args.directory

    is_parsing_site = not args.dont_parse_site
    is_parsing_txt = True

    valid_vins_file = vins_file + '_valid'
    dir_ = f'{root_dir}/{iteration}'
    xlsx_dir = f'{dir_}/output'

    data_dir = f"{dir_}/data"

    print('\nMain starts!\n')
    if is_parsing_site:
        print('\nCheck_validance starts!\n')
        check_validance(input_vins_file_=vins_file, valid_vins_file_=valid_vins_file)
        for req_type in required_types:
            print(f'\nParse_site for {req_type} starts! Wait for captcha.\n')
            parse_site(input_vins_file_=valid_vins_file, output_dir_=data_dir, checkType_=req_type)
    if is_parsing_txt:
        for req_type in required_types:
            print(f'\nConverting for {req_type} starts!\n')
            convert_txt_to_prq(input_dir_=data_dir, checkType_=req_type)
            convert_prq_to_xlsx(input_dir_=data_dir, output_xlsx_dir_=xlsx_dir, checkType_=req_type)
    print('\nAll done!')
