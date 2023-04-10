# Global_Irradiance_on_a_tilted_plane
import os
import pytz

from numpy import savetxt
from pvlib import solarposition, irradiance, location

# not needed in notebook
import pandas as pd
import numpy as np

CWD = os.getcwd()
CWD = CWD.replace(os.sep, '/')

########################
from Variables import filename, azimuth, albedo, tilt, tz

dbfile = pd.read_csv(CWD + '/weather_file/input/' + filename,
                     sep=',', header=1)  # importing csv file

with open(CWD + '/weather_file/input/' + filename,
          'r') as f:  # read the first line of csv (file main params are here)
    content = f.readlines()[0].rstrip()  # The rstrip() method removes any characters at the end a string
    list1 = list(content.split(","))

# Location
city, altitude, latitude, longitude = list1[1], int(list1[-1]), float(list1[-3]), float(list1[-2])

# extracting columns from dataframe

DNI = dbfile["DNI (W/m^2)"]
DHI = dbfile["DHI (W/m^2)"]
GHI = dbfile["GHI (W/m^2)"]

Drybulb = dbfile["Dry-bulb (C)"]
Pressure = dbfile["Pressure (mbar)"].mul(100)

Enoct = 800
NOCT = 45

# Global Irradiance calculation

times = pd.date_range('2005-01-01', '2006-01-01', closed="right",
                      freq='60min', tz=tz)  # closed right to shift time in 1 hour, with data

solpos = solarposition.get_solarposition(times, latitude, longitude, altitude, pressure=Pressure,
                                         method='nrel_numpy',
                                         temperature=Drybulb)
aoi = irradiance.aoi(tilt, azimuth, solpos.apparent_zenith, solpos.azimuth)

aoi = np.cos(np.radians(aoi))  # The solar incidence angle, θ, is the angle between the sun’s rays and the normal

Rd = (1 + np.cos(np.radians(tilt))) / 2  # diffuse transposition factor
Rr = (1 - np.cos(np.radians(tilt))) / 2  # transposition factor for ground reflection

DNI = DNI.tolist()
aoi = aoi.tolist()
E1 = np.multiply(DNI, aoi)

E1 = np.absolute(E1)

E2 = DHI * Rd + albedo * GHI * Rr
E2 = np.absolute(E2)

E = np.ceil(E1 + E2)  # Global irradiance

# Calculating cell temperature
ee = np.divide(E, Enoct)
ee1 = np.multiply(ee, (NOCT - 20))
tcell = np.add(Drybulb, ee1)

x = pd.DataFrame(data=E, columns=['Irradiance'])  # converting ndarray E to dataframe
x.index.names = ['Time']  # giving a name to an indexing column

x["temp"] = tcell  # simple as that, appening as a column series of temperatures OF THE CELL
x["temp"] = x["temp"].round(0)
lst = x["temp"].unique()
savetxt(CWD + '/weather_file/output/' + 'temperatures.txt', np.sort(lst))
savetxt(CWD + '/weather_file/output/' + 'Global_Irradiance_on_a_tilted_plane_new.csv', x, delimiter=',',
        fmt='%f')  # USE COMMA ON SOME PC
print(x['Irradiance'].sum())
print('File with global Irradiance successfully saved')
