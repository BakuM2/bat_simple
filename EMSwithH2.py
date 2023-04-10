import time
import os

start_time = time.time()

import pandas as pd
import numpy as np
from Variables import  grid_limitation, step_also_for_naming, battery_initial_charge, \
    limit_battery_max_charge, limit_battery_min_charge, battery_c_rate, battery_yes_no, customer

CWD = os.getcwd()
CWD = CWD.replace(os.sep, '/')

pd.options.mode.chained_assignment = None  # default='warn'


i = 0
k = 0

cols = ['Name', 'battery_size', 'consumed_per_year', 'solar_input', 'H2_production', 'a50kW_per_kg_of_H2',
        'ratio_of_kWsolar_kWcons',
        'NOT_from_grid', 'power from grid', 'energy_to_bat']

df = pd.DataFrame(columns=cols)
data = []

power = pd.read_csv(CWD+'/profiles/Gassner_kWh_profil.csv')


production = pd.read_csv(CWD+'/fixed_tilt/PV array/pvarray.csv', sep=';')
power['kWsolar'] = production['kWsolar']

power['Solar-cons'] = power['kWsolar'] - power['kWcons']
power['excess'] = 0
power['From_Grid'] = 0

power['battery_state_of_charge'] = [0 for i in range(0, power.shape[0])]
power['energy_to_bat'] = 0

for k in range(0, 25, 1):
    batsiz = k * 10  # production["kWp"][1]/5

    battery_max_charge = batsiz * limit_battery_max_charge  # 100000kW battery
    battery_min_charge = batsiz * limit_battery_min_charge
    SOD = batsiz * battery_c_rate  # was 200
    k = k + 1
    for hour in power['battery_state_of_charge'].keys():  # running a loop through all df
        if hour == power['battery_state_of_charge'].keys()[0]:
            power.loc[0, 'battery_state_of_charge'] = batsiz * battery_initial_charge
        else:
            if power['Solar-cons'][hour] > 0:  # excess of energy +
                if power['battery_state_of_charge'][
                    hour - 1] < battery_max_charge:  # battery is not fully charged added -1

                    if power['Solar-cons'][hour] > SOD:
                        power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][hour - 1] + SOD

                        if power['battery_state_of_charge'][
                            hour] >= battery_max_charge:  # to avoid battery overcharging
                            power['excess'][hour] = power['battery_state_of_charge'][hour] - battery_max_charge + (
                                    power['Solar-cons'][hour] - SOD)
                            power['battery_state_of_charge'][hour] = battery_max_charge
                            power['energy_to_bat'][hour] = abs(
                                power['battery_state_of_charge'][hour] - power['battery_state_of_charge'][
                                    hour - 1])  # calculating how much energy suplied to the battery

                        else:  # battery is not fully charged, but battery properties are not allowing to charge it more
                            power['excess'][hour] = power['Solar-cons'][hour] - SOD
                            power['energy_to_bat'][hour] = abs(
                                power['battery_state_of_charge'][hour] - power['battery_state_of_charge'][
                                    hour - 1])  # calculating how much energy suplied to the battery
                    else:  # all excess energy spend on battery charging
                        power['excess'][hour] = 0
                        power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][hour - 1] + \
                                                                 power['Solar-cons'][hour]
                        power['energy_to_bat'][hour] = abs(
                            power['battery_state_of_charge'][hour] - power['battery_state_of_charge'][
                                hour - 1])  # calculating how much energy suplied to the battery
                        if power['battery_state_of_charge'][hour] > battery_max_charge:
                            power['excess'][hour] = power['battery_state_of_charge'][hour] - battery_max_charge
                            power['battery_state_of_charge'][hour] = battery_max_charge
                            power['energy_to_bat'][hour] = abs(
                                power['battery_state_of_charge'][hour] - power['battery_state_of_charge'][
                                    hour - 1])  # calculating how much energy suplied to the battery
                else:
                    power['excess'][hour] = power['Solar-cons'][hour]
                    power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][hour - 1]


            else:  # lack of energy

                if power['kWsolar'][hour] <= 0 and power['battery_state_of_charge'][
                    hour - 1] == battery_min_charge:  # charging battery at night
                    power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][hour - 1] + SOD
                    power['From_Grid'][hour] = SOD + abs(power['Solar-cons'][hour])

                else:

                    if power['battery_state_of_charge'][
                        hour - 1] > battery_min_charge:  # battery is not fully charged, but can give electricity

                        if abs(power['Solar-cons'][hour]) < SOD:
                            power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][
                                                                         hour - 1] - abs(
                                power['Solar-cons'][hour])

                            if power['battery_state_of_charge'][
                                hour] < battery_min_charge:  # to avoid battery deep discharging
                                power['From_Grid'][hour] = battery_min_charge - power['battery_state_of_charge'][
                                    hour]
                                power['battery_state_of_charge'][hour] = battery_min_charge

                            else:  # power from grid is not needed
                                power['From_Grid'][hour] = 0

                        else:  # battery can't supply all required power
                            power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][
                                                                         hour - 1] - SOD

                            if power['battery_state_of_charge'][
                                hour] < battery_min_charge:  # to avoid battery deep discharging
                                power['From_Grid'][hour] = abs(
                                    (power['battery_state_of_charge'][hour - 1] - battery_min_charge) +
                                    power['Solar-cons'][hour])

                                power['battery_state_of_charge'][hour] = battery_min_charge

                            else:  # remaining power will be supplied from grid
                                power['From_Grid'][hour] = abs(power['Solar-cons'][hour]) - SOD
                    else:
                        power['From_Grid'][hour] = abs(
                            power['Solar-cons'][hour])  # - power['battery_state_of_charge'][hour] +
                        power['battery_state_of_charge'][hour] = battery_min_charge

    Namee = str(i * step_also_for_naming) + "kW_case_" + str(k)
    power.excess = np.where(power.excess > grid_limitation, grid_limitation, power.excess)
    # power.From_Grid = np.where(power.From_Grid<0,abs(power['Solar-cons']),power.From_Grid)

    consumed_per_year = power['kWcons'].sum()
    solar_input = power['kWsolar'].sum()
    H2_production = power['excess'].sum()
    a50kW_per_kg_of_H2 = power[
                             'excess'].sum() / 55000  # https://pv-magazine-usa.com/2020/03/26/electrolyzer-overview-lowering-the-cost-of-hydrogen-and-distributing-its-productionhydrogen-industry-overview-lowering-the-cost-and-distributing-production/
    ratio_of_kWsolar_kWcons = power['kWsolar'].sum() / power['kWcons'].sum()
    NOT_from_grid = 1 - power['From_Grid'].sum() / power['kWcons'].sum()
    power_from_grid = power['From_Grid'].sum()
    power_to_bat = power['energy_to_bat'].sum()

    values = [Namee, batsiz, consumed_per_year, solar_input, H2_production, a50kW_per_kg_of_H2,
              ratio_of_kWsolar_kWcons,
              NOT_from_grid, power_from_grid, power_to_bat]
    zipped = zip(cols, values)
    a_dictionary = dict(zipped)
    print(a_dictionary)
    data.append(a_dictionary)

    power.to_excel(
        CWD + '/fixed_tilt/' + "kW_case_" + str(k) + '.xlsx',
        sep=';', index=False,
        header=['DateTime', 'kWcons', 'kWsolar', 'Solar-cons', 'excess', 'From_Grid', 'battery_state_of_charge',
                'energy_to_bat'])
df = df.append(data, True)
df.to_csv(CWD + '/fixed_tilt/EMS_', sep=';', index=False, header=cols)
print("--- %s seconds ---" % (time.time() - start_time))
