import plotly.graph_objects as go
import pandas as pd
import numpy as np

pd.options.plotting.backend = "plotly"


# pd.set_option("display.max_rows", None,"display.max_columns", None)


def reader(path, path_pvsyst):
    pvsyst = pd.read_csv(path_pvsyst, delimiter=',')

    pvsyst['E_Grid'] = pvsyst['E_Grid'].astype(str).astype(float)
    pvsyst['E_Grid'] = np.where(pvsyst['E_Grid'] < 0, 0, pvsyst['E_Grid'])

    customer_profile = pd.read_excel(path)

    return customer_profile, pvsyst

def annual_range(date_str, hourly_periods, days):
    start = pd.to_datetime(date_str) - pd.Timedelta(days)
    drange = pd.date_range(start, periods=hourly_periods, freq='H').round('min') #rounding to exact minute
    drange = drange.strftime("%d.%m.%Y %H:%M:%S") #changing representaion format
    return drange

def comparison(customer_profile, pvsyst,save_path,drange):
    comparison = pd.DataFrame()

    comparison['consumption'] = customer_profile['sum']
    comparison['production'] = pvsyst['E_Grid']

    comparison['difference'] = comparison['consumption'].values - comparison['production'].values
    comparison['for_calc'] = np.where(comparison['difference'] > 0, pvsyst['E_Grid'], comparison['consumption'])
    share = round(sum(comparison['for_calc']) / sum(comparison['consumption']) * 100,1)
    comparison.insert(loc=0, column='Time', value=drange)
    comparison.to_excel(save_path, index=False)
    return comparison, share


def figure(customer_profile ,pvsyst,n1,n2,first_name,second_name,share,save_path2):#
    '''n1,n2 is the window range
    first_name,second_name are df columns names, find them in advance'''
    fig = go.Figure()
    fig.add_scatter(x=customer_profile['Time'][n1:n2], y=customer_profile['sum'][n1:n2],fill='tozeroy', #fill down to xaxis

                         mode='lines')
    fig.add_scatter(x=customer_profile['Time'][n1:n2], y=pvsyst['E_Grid'],fill='tozeroy')

    fig['data'][0]['name'] = first_name
    fig['data'][1]['name'] =second_name
    title = {'text': title_name,
             'y': 0.95,
             'x': 0.5,
             'xanchor': 'center',
             'yanchor': 'top'}

    fig.update_layout(
        xaxis_title="Time, days",
        yaxis_title="Energy, kWh",
        title=title,
        legend_title="Legend",
        legend=dict(
            x=0.85,
            y=0.92,

            title_font_family="Times New Roman",
            font=dict(
                family="Courier",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=1
        ), xaxis_rangeslider_visible=False)
    fig.add_annotation(text=f'Customer consumption is {share} %% covered ',
                       align='left',
                       showarrow=False,
                       xref='paper',
                       yref='paper',
                       x=0.85,
                       y=0.88,
                       bgcolor="LightSteelBlue",
                       bordercolor="Black",
                       borderwidth=1)
    fig.update_traces(opacity=1)
    fig.show()
    fig.write_html(save_path2)

if __name__ == '__main__':
    n1 = 0

    days = 365
    n2 = 24 * days    # *4 bcoz it is 15mins
    hourly_periods = n2
    date_str = '01.01.2021'
    path_pvsyst = 'C:/Users/d.bakumenko/Desktop/Romania/Energy analysis/Pythin/Chisenau Cris_Project_VCF_HourlyRes_0.csv'
    consumption_path = 'C:/Users/d.bakumenko/Desktop/Romania/Energy analysis/Pythin/whole_year_Curbe de sarcina HAI EXTRUSION.xlsx'
    save_path='C:/Users/d.bakumenko/Desktop/Romania/Energy analysis/Pythin/Curbe de sarcina hai.xlsx'
    save_path2 = 'C:/Users/d.bakumenko/Desktop/Romania/Energy analysis/Pythin/Curbe de sarcina hai.html'
    first_name = 'actual profile'
    second_name = 'pvsyst'
    title_name = "Curbe de sarcina hai"

    x, graph = reader(consumption_path, path_pvsyst)
    drange=annual_range(date_str, hourly_periods, days)
    comp, share = comparison(x, graph,save_path,drange)

    figure(x, graph, n1, n2, first_name,second_name, share,save_path2)# save_path)
