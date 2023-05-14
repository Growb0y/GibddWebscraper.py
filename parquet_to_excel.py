import pathlib
import pandas as pd
from resources.lists import needed_indexes_history, needed_indexes_dtp


def convert_prq_to_xlsx(input_dir_, output_xlsx_dir_, checkType_):
    """
    функция конвертации файлов .parquet в .xlsx
    :param input_dir_: string - название папки c файлами .parquet
    :param output_xlsx_dir_: string - название папки, куда записывется выходной файл
    :param checkType_: string - вид данных (history/dtp)
    :return: None (функция записывает данные в файл)
    """

    pathlib.Path(output_xlsx_dir_).mkdir(parents=True, exist_ok=True)

    dir_ = f'{input_dir_}/{checkType_}'

    new_df = pd.DataFrame()
    new_df_null = pd.DataFrame()

    dir_type = checkType_

    PRQ_FILE = f"{dir_}/data.parquet"
    PRQ_FILE_NULL = f"{dir_}/data_null.parquet"

    df_from_prq = pd.read_parquet(PRQ_FILE, engine='pyarrow')
    if dir_type == "dtp":
        df_from_prq['Accidents'] = df_from_prq['Accidents'].apply(lambda x: x if x is not None else [])
    if dir_type == "history":
        df_from_prq['Ownership Periods'] = df_from_prq['Ownership Periods'].apply(lambda x: x if x is not None else [])

    if dir_type == "history":

        indexes_dict = {'VIN': []}
        needed_indexes = needed_indexes_history
        for index in needed_indexes:
            indexes_dict[index] = []
        for i, row in df_from_prq.iterrows():
            for acc in row['Ownership Periods']:
                indexes_dict['VIN'].append(row['VIN'])
                for index in row['Ownership Periods'][0]:
                    indexes_dict[index].append(acc[index])
        new_indexes_dict = {}
        for key, value in indexes_dict.items():
            if len(value) != 0:
                new_indexes_dict[key] = value
        new_df = pd.DataFrame(new_indexes_dict)

    if dir_type == "dtp":

        indexes_dict = {'VIN': []}
        needed_indexes = needed_indexes_dtp
        for index in needed_indexes:
            indexes_dict[index] = []
        for i, row in df_from_prq.iterrows():
            for acc in row['Accidents']:
                indexes_dict['VIN'].append(row['VIN'])
                for index in needed_indexes:
                    indexes_dict[index].append(acc[index])
        new_df = pd.DataFrame(indexes_dict)

        indexes_dict_null = {'VIN': []}
        for i, row in df_from_prq.iterrows():
            if len(row['Accidents']) == 0:
                indexes_dict_null['VIN'].append(row['VIN'])
        new_df_null = pd.DataFrame(indexes_dict_null)

    df_from_prq_null = pd.read_parquet(PRQ_FILE_NULL, engine='pyarrow')

    # Запись результатов в Excel
    with pd.ExcelWriter(f'{output_xlsx_dir_}/{checkType_}.xlsx') as writer:
        new_df.to_excel(writer, sheet_name='Данные')
        if checkType_ == 'dtp':
            new_df_null.to_excel(writer, sheet_name='Не попадали в ДТП')
        if checkType_ == 'history':
            df_from_prq_null.to_excel(writer, sheet_name='Не найдены в системе')
