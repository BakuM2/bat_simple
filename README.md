# Bat simple
That's a simple code, that does battery evaluation, based on customer load profile and weather data,taken from meteonorm database.
To succesfully perform a simulation run files one after another, as described below.

## Fill the variable
Open `Variables.py` file and set following data:
- tilt
- grid_limitation 
- limit_battery_min_charge 
- limit_battery_max_charge 
- bat_efficiency
- battery_c_rate

## Process weather file for the future analysis
`irradiance_and_tempcreator.py` 

## IV curve
`single_module.py` generates single module IV curve, based on the weather data file above change the Panel_name from: `sam-library-cec-modules-2019-03-05.csv`

## PV array
`pvplantmulti.py` calculates pv array, based on inputed `Power_range`. Range is in Watts, max tested was 1MW

## kW to Wh
`kw_to_kwh.py` converts kW customer profile to Wh 

> output is in Watt-hours!!!!
>

## Battery behaviour
`EMSbat.py` slowly, but steadily calculates battery behaviour in 1hr resolution, also returns an output file `EMS_.csv`, containing summary of all simulations

## Diagram
`graphs.py` creates diagram of selected case
