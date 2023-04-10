customer = 'Name'
filename = 'Wels-hour.csv'

albedo = 0.2
tilt = 35
azimuth = 180  # 90 W, 180 S, 270 E

autarchy = 0.7

panel_degradation_after_year_one = 0.97
tz = "Europe/Amsterdam"
lifetime = 30
grid_limitation = 20000

step_also_for_naming = 20

battery_yes_no = 11  # 11 mean yes, 1 no
battery_initial_charge = 400
limit_battery_max_charge = 900
limit_battery_min_charge = 200
battery_c_rate = 500  # 1000 is 1
bat_efficiency = 0.9
battery_efficiency = 0.9 * 0.9

storage_size = 1  # month
hours_of_electrolyser_full_work = 6
compression_rate_bars = 30
fuel_consumption = 2500
diesel_price = 2.615  # https://www.globalpetrolprices.com/Austria/diesel_prices/

batteryprice = 900
electrolyserprice = 1000
storageprice = 450  #
water_price = 3.5
price_of_sold_electricity = 0.25  # 0.25
price_of_bought_electricity = 0.3  # 0.3
debt = 0.7  # equity = 1 - debt
corporate_tax = 0.23
discount_rate = 0.05

Opex_from_Capex = 0.02  # %
Opex_from_Capex_H2 = 0.03
