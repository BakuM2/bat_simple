import time
import os
import pandas as pd
import numpy as np
from Variables import grid_limitation, step_also_for_naming, battery_initial_charge, \
    limit_battery_max_charge, limit_battery_min_charge, battery_c_rate, battery_yes_no, customer

start_time = time.time()
CWD = os.getcwd()
CWD = CWD.replace(os.sep, '/')

pd.options.mode.chained_assignment = None  # default='warn'

max_bat = 100  # size in KWh *1000
i = 0
k = 0
profile_name = "profile"
cols = ['Name', 'battery_size', 'consumed_per_year', 'solar_input',
        'ratio_of_kWsolar_kWcons',
        'NOT_from_grid', 'power from grid', 'energy_to_bat', 'energy lost']

df = pd.DataFrame(columns=cols)
data = []

power = pd.read_csv(CWD + f'/Profiles/{profile_name}.csv', sep=';')

production = pd.read_csv(CWD + '/fixed_tilt/PV array/pvarray.csv', sep=';')
power['kWsolar'] = production['kWsolar']

power['Solar_cons'] = power['kWsolar'] - power['kWcons']
power['excess'] = 0
power['From_Grid'] = 0

power['battery_state_of_charge'] = [0 for i in range(0, power.shape[0])]
power['energy_to_bat'] = 0
power['energy_lost'] = 0


def front(k):
    '''wins few milisecs, originally it was right after ____for k in range loop____'''
    batsiz = k * 10  # production["kWp"][1]/5
    battery_max_charge = batsiz * limit_battery_max_charge  # 100000kW battery
    battery_min_charge = batsiz * limit_battery_min_charge
    SOD = batsiz * battery_c_rate  # was 200
    BMC_sod = - battery_max_charge - SOD
    return batsiz, battery_max_charge, battery_min_charge, SOD, BMC_sod


for k in range(0, max_bat, 1):
    time_loop = time.time()
    batsiz, battery_max_charge, battery_min_charge, SOD, BMC_sod = front(k)
    k = k + 1
    power.loc[0, 'battery_state_of_charge'] = batsiz * battery_initial_charge
    for hour in power['battery_state_of_charge'].keys()[
                1:len(power['battery_state_of_charge'])]:  # running a loop through all df
        pbschm1 = power['battery_state_of_charge'][hour - 1]
        psc = power['Solar_cons'][hour]
        if psc > 0:  # excess of energy +
            if power['battery_state_of_charge'][
                hour - 1] < battery_max_charge:  # battery is not fully charged added -1

                if psc > SOD:
                    power['battery_state_of_charge'][hour] = power['battery_state_of_charge'][hour - 1] + SOD
                    pbsc = power['battery_state_of_charge'][hour]

                    if power['battery_state_of_charge'][hour] >= battery_max_charge:  # to avoid battery overcharging
                        power['excess'][hour] = pbsc + psc + BMC_sod
                        power['battery_state_of_charge'][hour] = battery_max_charge
                        # power['energy_to_bat'][hour] = abs(
                        #     power['battery_state_of_charge'][hour] - power['battery_state_of_charge'][
                        #         hour - 1])  # calculating how much energy suplied to the battery

                    else:  # battery is not fully charged, but battery properties are not allowing to charge it more
                        power['excess'][hour] = psc - SOD
                    power['energy_to_bat'][hour] = abs(
                        power['battery_state_of_charge'][
                            hour] - pbschm1)  # calculating how much energy suplied to the battery
                else:  # all excess energy spend on battery charging
                    power['excess'][hour] = 0

                    power['battery_state_of_charge'][hour] = pbschm1 + psc
                    power['energy_to_bat'][hour] = abs(
                        power['battery_state_of_charge'][
                            hour] - pbschm1)  # calculating how much energy suplied to the battery

                    if power['battery_state_of_charge'][hour] > battery_max_charge:
                        power['excess'][hour] = power['battery_state_of_charge'][hour] - battery_max_charge
                        power['battery_state_of_charge'][hour] = battery_max_charge
                        power['energy_to_bat'][hour] = abs(power['battery_state_of_charge'][
                                                               hour] - pbschm1)  # calculating how much energy suplied to the battery
            else:
                power['excess'][hour] = psc
                power['battery_state_of_charge'][hour] = pbschm1


        else:  # lack of energy
            psc = abs(power['Solar_cons'][hour])

            if power['kWsolar'][hour] <= 0 and pbschm1 == battery_min_charge:  # charging battery at night
                power['battery_state_of_charge'][hour] = pbschm1 + SOD
                power['From_Grid'][hour] = SOD + psc

            else:

                if pbschm1 > battery_min_charge:  # battery is not fully charged, but can give electricity

                    if psc < SOD:
                        power['battery_state_of_charge'][hour] = pbschm1 - psc

                        if power['battery_state_of_charge'][
                            hour] < battery_min_charge:  # to avoid battery deep discharging
                            power['From_Grid'][hour] = battery_min_charge - power['battery_state_of_charge'][
                                hour]
                            power['battery_state_of_charge'][hour] = battery_min_charge
                        else:  # power from grid is not needed
                            power['From_Grid'][hour] = 0

                    else:  # battery can't supply all required power
                        power['battery_state_of_charge'][hour] = pbschm1 - SOD

                        if power['battery_state_of_charge'][
                            hour] < battery_min_charge:  # to avoid battery deep discharging
                            power['From_Grid'][hour] = abs(pbschm1 - battery_min_charge) + psc
                            power['battery_state_of_charge'][hour] = battery_min_charge

                        else:  # remaining power will be supplied from grid
                            power['From_Grid'][hour] = psc - SOD
                else:
                    power['From_Grid'][hour] = psc  # - power['battery_state_of_charge'][hour] +
                    power['battery_state_of_charge'][hour] = battery_min_charge

    Namee = str("case_" + str(k))
    power.excess = np.where(power.excess > grid_limitation, grid_limitation, power.excess)
    power['energy_lost'] = power.Solar_cons - power.excess - power.energy_to_bat
    power['energy_lost'] = np.where(power['energy_lost'] > 0, power['energy_lost'], 0)
    consumed_per_year = power['kWcons'].sum() / 1000
    solar_input = power['kWsolar'].sum() / 1000

    ratio_of_kWsolar_kWcons = power['kWsolar'].sum() / power['kWcons'].sum()
    NOT_from_grid = 1 - power['From_Grid'].sum() / power['kWcons'].sum()
    power_from_grid = power['From_Grid'].sum() / 1000
    power_to_bat = power['energy_to_bat'].sum() / 1000
    power_lost = power['energy_lost'].sum() / 1000
    values = [Namee, batsiz, consumed_per_year, solar_input,
              ratio_of_kWsolar_kWcons,
              NOT_from_grid, power_from_grid, power_to_bat, power_lost]
    zipped = zip(cols, values)
    a_dictionary = dict(zipped)
    print(a_dictionary)
    data.append(a_dictionary)

    power.to_excel(
        CWD + '/fixed_tilt/battery/bat_size' + str(k) + '.xlsx',
        index=False,
        header=['DateTime', 'kWcons', 'kWsolar', 'Solar_cons', 'excess', 'From_Grid', 'battery_state_of_charge',
                'energy_to_bat', 'energy_lost'])
    print("--- %s seconds ---" % (time.time() - time_loop))
df = df.append(data, True)

df.to_csv(CWD + '/fixed_tilt/EMS_.csv', sep=';', index=False, header=cols)
print("--- %s seconds ---" % (time.time() - start_time))
