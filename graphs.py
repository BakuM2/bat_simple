import plotly.express as px
import pandas as pd
import numpy as np

import os

CWD = os.getcwd()
sim_name = "bat_size21"
# settings
pd.options.plotting.backend = "plotly"
x = pd.read_excel(CWD + f'/Fixed tilt/battery/{sim_name}.xlsx')  # x axis profile
graph = pd.read_excel(CWD + f'/Fixed tilt/battery/{sim_name}.xlsx')

trc = 40000

graph.rename(columns={'excess': 'to_grid'}, inplace=True)

graph['excess2'] = graph['to_grid']  # creating 2 equal columns, to work with them separately

graph.excess2 = np.where(graph.to_grid.eq(20000), graph.Solar_cons, graph.excess2)
graph['From_Grid'] = np.where(graph['From_Grid'] > trc, trc, graph['From_Grid'])
pd.set_option("display.max_rows", None, "display.max_columns", None)

n1 = 0
n2 = 24 * 365

fig = px.line(x=x['DateTime'][n1:n2], y=[graph['kWcons'][n1:n2], graph['kWsolar'][n1:n2], graph['From_Grid'][n1:n2],
                                         graph['energy_to_bat'][n1:n2], graph['energy_lost'][n1:n2],
                                         graph['battery_state_of_charge'][n1:n2]])

fig['data'][0]['name'] = 'Consumed'
fig['data'][1]['name'] = 'Supplied from PV'

fig['data'][2]['name'] = 'Supplied from Grid'
fig['data'][3]['name'] = 'Energy delivered to battery'
fig['data'][4]['name'] = 'Energy lost, due to the grid limitation'
fig['data'][5]['name'] = 'Battery state of charge'

fig.update_layout(
    xaxis_title="Time, days",
    yaxis_title="Energy, kWh",
    legend_title="Legend",
    legend=dict(
        x=0.8,
        y=1,
        traceorder="reversed",
        title_font_family="Times New Roman",
        font=dict(
            family="Courier",
            size=12,
            color="black"
        ),
        bgcolor="LightSteelBlue",
        bordercolor="Black",
        borderwidth=1
    )
)

fig.show()
fig.write_html("battery_profile.html")
