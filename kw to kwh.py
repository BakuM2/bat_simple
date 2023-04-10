import pandas as pd
import os

CWD = os.getcwd()
CWD = CWD.replace(os.sep, '/')
profile_name = "profile"
path = CWD + f'/Profiles/Input/{profile_name}.xlsx'
N = 4  # for 15 mins

date_str = '1/1/2022'  # means all 2021
hourly_periods = 8760
days = 365
save_path = CWD + f'/Profiles/output/{profile_name}_kWh.csv'
conversion = 1000


def new_df_creator(path, N):
    file_to_convert = pd.read_excel(path)

    file_to_convert = file_to_convert / N  # Power to energy
    file_to_convert = file_to_convert.groupby(
        file_to_convert.index // N).sum()  # grouping by hours, since we know that all is in 15 min res
    file_to_convert = file_to_convert * conversion

    return file_to_convert


def annual_range(date_str, hourly_periods, days):
    start = pd.to_datetime(date_str)

    drange = pd.date_range(start, periods=hourly_periods, freq='H')

    return drange


def merger_and_saver(file_to_convert, drange):
    file_to_convert.insert(loc=0, column='Datum', value=drange)
    file_to_convert.columns = file_to_convert.columns.str.replace("kW", "kWh")
    file_to_convert.columns = file_to_convert.columns.str.replace("Power", "kWcons")

    file_to_convert.to_csv(save_path, index=False, sep=';')


if __name__ == '__main__':
    new_df = new_df_creator(path, N)
    drange = annual_range(date_str, hourly_periods, days)
    merger_and_saver(new_df, drange)
