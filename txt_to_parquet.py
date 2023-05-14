import json
import codecs
import pandas as pd
from resources.lists import replacing_dict, needed_indexes_dtp, needed_indexes_history


def convert_txt_to_prq(input_dir_, checkType_):
    """
    функция конвертации файлов  c данными с сайта (.txt) в .parquet
    :param input_dir_: string - название папки c файлами .txt
    :param checkType_: string - вид данных (history/dtp)
    :return: None (функция записывает данные в файл)
    """

    dir_ = f'{input_dir_}/{checkType_}'

    def replace_using_dict(string_, replacing_dict_):
        for line in replacing_dict_:
            condition = line
            replacement = replacing_dict_[line]
            string_ = string_.replace(condition, replacement)
        return string_

    def createNewDfRow(l_, needed_indexes_):
        if l_['Accidents']:
            new_list = []
            for dict_ in l_['Accidents']:
                new_list.append(dict((key, value) for key, value in dict_.items() if key in needed_indexes_))
            new_seria = pd.Series([new_list])
            return new_seria
        else:
            return pd.Series([[]])

    def createNewDfRow2(l_, needed_indexes_):
        if l_['ownershipPeriods']['ownershipPeriod']:
            new_list = []
            for dict_ in l_['ownershipPeriods']['ownershipPeriod']:
                new_list.append(dict((key, value) for key, value in dict_.items() if key in needed_indexes_))
            new_seria = pd.Series([new_list])
            return new_seria
        else:
            return pd.Series([[]])

    # txt to json

    txt_file = f"{dir_}/data.txt"
    json_file = f"{dir_}/data.json"

    f = codecs.open(txt_file, "r", "utf_8_sig")
    lines = f.readlines()
    f.close()

    d = {}
    for l in lines:
        num, vin, info = l.split(" ::: ")
        num_vin = num + "_" + vin
        info = replace_using_dict(info, replacing_dict)
        d[num_vin] = json.loads(info.replace('"', "*")
                                .replace("{}", '""')
                                .replace("'", '"'))

    d = dict(sorted(d.items(), key=lambda item: int(item[0].split("_")[0])))

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

    # json to parquet

    json_file = f"{dir_}/data.json"
    prq_file = f"{dir_}/data.parquet"
    prq_file_null = f"{dir_}/data_null.parquet"

    df_json = pd.read_json(json_file).T
    if 'RequestResult' in df_json:
        df = pd.DataFrame(df_json['RequestResult'])
    else:
        df = pd.DataFrame(df_json['status'])
        df['RequestResult'] = pd.Series(dtype='object')
        df['RequestResult'] = [None for _ in range(len(df))]
    df['index'] = df.index
    df['VIN'] = df['index'].apply(lambda l: l.split("_")[1])
    df = df.drop('index', axis='columns')
    df = df.reset_index(drop=True)

    df_na = df[df.RequestResult.isna()]
    df_na = df_na.drop('RequestResult', axis='columns')

    df_na = df_na.assign(Error_Status="Не найден")
    df_na.to_parquet(prq_file_null)

    if checkType_ == "history":
        df = df.applymap(lambda x: {'ownershipPeriods': {'ownershipPeriod': []}} if pd.isna(x) else x)
        df['Ownership Periods'] = df['RequestResult'].apply(createNewDfRow2, needed_indexes_=needed_indexes_history)
    elif checkType_ == "dtp":
        df['Accidents'] = df['RequestResult'].apply(createNewDfRow, needed_indexes_=needed_indexes_dtp)
    print("\ndf: ", df)

    df = df.drop('RequestResult', axis='columns')

    df.to_parquet(prq_file)

    df_from_prq = pd.read_parquet(prq_file, engine='pyarrow')
    print("\nParquet:")
    print(df_from_prq)
