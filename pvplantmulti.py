import os
import pvlib
from pvlib import pvsystem, inverter  # I don't know, sometimes jupiter can't find inverter module
import sys
import numpy as np
# not needed in notebook
import pandas as pd
import math

CWD = os.getcwd()
CWD = CWD.replace(os.sep, '/')

pd.set_option("display.max_rows", None, "display.max_columns", None)  # print the whole DF

panelfile = pd.read_csv(CWD + '/sam_library/sam-library-cec-modules-2019-03-05.csv')  # df with 25355 different panels
inverterfile = pd.read_csv(CWD + '/sam_library/sam-library-cec-inverters-2019-03-05.csv')
Irradiance = pd.read_csv(CWD + '\Weather file\output\single_module.csv', sep=';')

sapm_inverters2 = pvsystem.retrieve_sam('cecinverter')

Panel_name = 'SunPower SPR-X22-475-COM'  # input(

Power_range = [180000, 230000]


# that function replaces unwanted symbols to _

def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the strings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


stdoutOrigin = sys.stdout
sys.stdout = open(CWD + "/fixed_tilt/PV array/PV_plant_info.txt", "w")  # saving screen output ot a txt file

param = panelfile[panelfile['Name'] == Panel_name]  # df with that exact panel, for integers

vals = panelfile[panelfile[
                     'Name'] == Panel_name]  # df with that exact panel

############################FILE OPTIMIZATION#######################################


inverterfile['Vdcmax'] = pd.to_numeric(inverterfile['Vdcmax'], errors='coerce').fillna(0,
                                                                                       downcast='infer')
inverterfile['Pdco'] = pd.to_numeric(inverterfile['Pdco'], errors='coerce').fillna(0, downcast='infer')

# Voc calculation

Voc25 = float(vals.iloc[0]['V_oc_ref'])  # reference of panel open circuit voltage
Koc = float(vals.iloc[0]['beta_oc']) / 100  # PV Temperature Coefficient of voltage
VocTmin = Voc25 * (1 + Koc * (-35))
VocMPP = float(vals.iloc[0]['V_mp_ref'])  # reference of panel MPP voltage
VocTmax = VocMPP * (1 + 2 * Koc * 70)

#########################ARRAYS CALCUALTIONS#######################################
import random

Array = pd.DataFrame()

# Inverter selection
selectI = inverterfile[(inverterfile['Pdco'] >= Power_range[0]) & (inverterfile['Pdco'] <= Power_range[1])]

if len(selectI) > 1:
    a = random.randint(0, len(selectI))
    if a > len(selectI):
        a = len(selectI) - 1
        if a == 0:
            a = 1
else:
    a = 1

seldf = selectI.iloc[a - 1]  # Inverter selection

VinMin30 = float(seldf['Mppt_low'])
n30min = math.ceil(VinMin30 / VocTmax)

n30max = math.floor(seldf['Vdcmax'] / VocTmin)

n30stings = math.floor(float(seldf['Idcmax']) / float(vals.iloc[0]['I_sc_ref']) / 1.25)

Array["irrad"] = Irradiance['Irrad']
Array["temp"] = Irradiance['temp']
Array['v_mp'] = n30min * Irradiance['v_mp'].fillna(0)
Array['i_mp'] = n30stings * Irradiance['i_mp'].fillna(0)
Array['p_mp'] = Array['v_mp'] * Array['i_mp']

aa = []
invname = str()


def inv_name_func(aa, invname):
    aa = seldf['Name']
    aa = replaceMultiple(aa, [' ', '(', ')', '+', ':', '-', '.', '[', ']', '/'], '_')

    invname = sapm_inverters2.loc[:, aa]  # inverter as an object, with nested parameters

    ac = pvlib.inverter.sandia(Array['v_mp'], Array['p_mp'], invname)
    ac[ac < 0] = 0
    annual_energy = ac.sum()
    return aa, annual_energy, ac


aa, invname, ac = inv_name_func(aa, invname)

if invname == 0:
    seldf = selectI.iloc[0]
    if "[208V]" or 'EQX0250UV480TN_(P)' in seldf['Name']:
        seldf = selectI.iloc[1]

    aa, invname, ac = inv_name_func(aa, invname)

print("Simullation ", "n panels", n30min, "\n n strings ", n30stings, '\n', invname, "Wh")
print("Annual energy produced in MWh: ", round(invname / 1000000, 3), "MWh", '\n')
Array['kWsolar'] = ac

np.savetxt(CWD + '/fixed_tilt/PV array/pvarray.csv', Array, header="irad;temp;v_mp;i_mp;p_mp;kWsolar", delimiter=';',
           fmt='%.0f', comments='')

sys.stdout.close()
sys.stdout = stdoutOrigin
