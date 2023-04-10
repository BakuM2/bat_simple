import os
import pvlib
from pvlib import pvsystem, inverter
import sys
import numpy as np
import pandas as pd

CWD = os.getcwd()
CWD = CWD.replace(os.sep, '/')

panelfile = pd.read_csv(CWD + '/sam_library/sam-library-cec-modules-2019-03-05.csv')  # df with 25355 different panels

Panel_name = 'SunPower SPR-X22-475-COM'  # input(

param = panelfile[panelfile['Name'] == Panel_name]  # df with that exact panel, for integers

vals = panelfile[panelfile[
                     'Name'] == Panel_name]  # df with that exact panel
pd.set_option("display.max_rows", None, "display.max_columns", None)  # print the whole DF

param = param.drop(['Name', 'Technology', 'BIPV', 'Version', 'Date'], axis=1)
param = param.astype(float)

# Module parameters for Selected module (see Panel_name):
parameters = {
    'Name': vals['Name'],
    'BIPV': vals['BIPV'],
    'Date': vals['Date'],
    'T_NOCT': param['T_NOCT'].item(),
    'A_c': param['A_c'].item(),
    'N_s': param['N_s'].item(),
    'I_sc_ref': param['I_sc_ref'].item(),
    'V_oc_ref': param['V_oc_ref'].item(),
    'I_mp_ref': param['I_mp_ref'].item(),
    'V_mp_ref': param['V_mp_ref'].item(),
    'alpha_sc': param['alpha_sc'].item(),
    'beta_oc': param['beta_oc'].item(),
    'a_ref': param['a_ref'].item(),
    'I_L_ref': param['I_L_ref'].item(),
    'I_o_ref': param['I_o_ref'].item(),
    'R_s': param['R_s'].item(),
    'R_sh_ref': param['R_sh_ref'].item(),
    'Adjust': param['Adjust'].item(),
    'gamma_r': param['gamma_r'].item(),
    'Version': vals['Version'],
    'PTC': param['PTC'].item(),
    'Technology': vals['Technology']
}

cases = []  # that list is for all possible combinations of temperatures and respective irradiances

with open(CWD + '/weather_file/output/' + "temperatures.txt") as f:
    temperatures = [int(float(x)) for x in f.read().split()]

for i in range(len(temperatures)):
    rang = [(min(n, 1000), temperatures[i]) for n in range(100, 1001, 1)]
    cases += rang

conditions = pd.DataFrame(cases, columns=['Geff', 'Tcell'])

# adjust the reference parameters according to the operating
# conditions using the De Soto model for cec modules
IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_cec(
    conditions['Geff'],
    conditions['Tcell'],
    alpha_sc=parameters['alpha_sc'],
    a_ref=parameters['a_ref'],
    I_L_ref=parameters['I_L_ref'],
    I_o_ref=parameters['I_o_ref'],
    R_sh_ref=parameters['R_sh_ref'],
    R_s=parameters['R_s'],
    Adjust=parameters['Adjust'],
    EgRef=1.121,  # bandgap energy C-Si
    dEgdT=-0.0002677,
    # The empirical constant 0.0002677 is representative of silicon cells at typical operating temperatures
    irrad_ref=1000,
    temp_ref=25
)

# plug the parameters into the SDE and solve for IV curves:
curve_info = pvsystem.singlediode(
    photocurrent=IL,
    saturation_current=I0,
    resistance_series=Rs,
    resistance_shunt=Rsh,
    nNsVth=nNsVth,
    ivcurve_pnts=100,
    method='lambertw'
)

ranges1 = pd.Series(range(100, 1001))

ranges2 = pd.concat([ranges1] * len(temperatures)).reset_index(
    drop=True)  # repeat 1 range 7 times , reset is important to reset indexing

a = (pd.DataFrame({
    'i_sc': curve_info['i_sc'],
    'v_oc': curve_info['v_oc'],
    'i_mp': curve_info['i_mp'],
    'v_mp': curve_info['v_mp'],
    'p_mp': curve_info['p_mp'],
}))

a['Irrad'] = ranges2  # append df ranges1 to df "a" as a column, however num is last column

b = np.repeat(temperatures, 901)

a["temp"] = b

# Now load Irradiance data

dbfile1 = pd.read_csv(CWD + '/weather_file/output/Global_Irradiance_on_a_tilted_plane_new.csv',
                      names=['Irrad', "temp"], header=None)  # importing csv file
# pd.set_option('display.float_format', lambda x: '%.0f' % x)

Irradiance = pd.merge(dbfile1,
                      a,
                      on=['Irrad', "temp"],
                      how='left')  # vlookup function

Irradiance['p_mp'] = Irradiance['p_mp'].fillna(0)
Irradiance['i_mp'] = Irradiance['i_mp'].fillna(0)
Irradiance['v_mp'] = Irradiance['v_mp'].fillna(0)
Irradiance['i_sc'] = Irradiance['i_sc'].fillna(0)
Irradiance['v_oc'] = Irradiance['v_oc'].fillna(0)

Energy_module_year = Irradiance['p_mp'].sum()  # sum all values in the row

# Savin results for a single module
np.savetxt('weather_file\output\single_module.csv', Irradiance, delimiter=';', fmt='%f',
           header='Irrad;temp;p_mp;i_mp;v_mp;i_sc;v_oc', comments='')  # USE COMMA ON SOME PCs
