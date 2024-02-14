import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import requests
from io import StringIO

# Function to filter data by date
def filter_data_by_date(file_content, target_date):
    lines = file_content.split('\n')

    filtered_data = []
    is_target_date = False

    for line in lines:
        if target_date in line:
            is_target_date = True
        elif 'Observations at' in line:
            is_target_date = False

        if is_target_date:
            filtered_data.append(line)

    return filtered_data

# Function to create DataFrame from filtered data
def dataframemaker(file_content, target_date):
    filtered_data = filter_data_by_date(file_content, target_date)
    split_data = [line.split() for line in filtered_data]

    empty_columns = [3, 4, 5, 6, 7, 8, 9, 10]
    for row in split_data[5:]:
        for col_index in empty_columns:
            if len(row) <= col_index:
                row.append(np.nan)

    df = pd.DataFrame(split_data[5:], columns=split_data[2])
    df = df.iloc[2:]
    df = df.iloc[:-33]
    df.reset_index(drop=True, inplace=True)
    df2 = df.dropna()
    return df2

# Function to plot data
def plot_data(selvar, year, month, date):
    dt = datetime.datetime(year, month, date, 0)
    casedate = dt.strftime('%HZ %d %b %Y')
    caseyear = dt.strftime('%Y')
    datelist1 = [(dt - datetime.timedelta(days=n)).strftime('%HZ %d %b %Y') for n in range(7)]
    datelist2 = [(dt + datetime.timedelta(days=n)).strftime('%HZ %d %b %Y') for n in range(7)]
    datelist = datelist1 + datelist2

    yearlist1 = [(dt - datetime.timedelta(days=n)).strftime('%Y') for n in range(7)]
    yearlist2 = [(dt + datetime.timedelta(days=n)).strftime('%Y') for n in range(7)]
    yearlist = yearlist1 + yearlist2

    data = pd.DataFrame(columns=['Parameter', 'Pressure'])
    for yy, dateofdata, cols, tlag in zip(yearlist, datelist,
                                          ['#65018c', '#0a04b5', '#0546fa', '#0273e3', '#02ced1', '#05f293', '#3ee302',
                                           '#fafa02', '#e6c005', '#fcaa05', '#e37302', '#ff5703', '#e62102', '#f7027d'],
                                          [-7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7]):
        try:
            url = f'https://raw.githubusercontent.com/alfuadi/sajiva/main/nffn/nffn_{yy}.out'
            file_content = requests.get(url).text
            df = dataframemaker(file_content, dateofdata)
            if selvar == 1:
                varname = 'Temperature'
                param = 'TEMP'
            elif selvar == 2:
                varname = 'Dewpoint'
                param = 'DWPT'
            elif selvar == 3:
                varname = 'Frost Point'
                param = 'FRPT'
            elif selvar == 4:
                varname = 'RH'
                param = 'RELH'
            elif selvar == 5:
                varname = 'RH respect to Ice'
                param = 'RELI'
            elif selvar == 6:
                varname = 'Mixing Ratio'
                param = 'MIXR'
            elif selvar == 7:
                varname = 'Wind Direction'
                param = 'DRCT'
            elif selvar == 8:
                varname = 'Wind Speed'
                param = 'SKNT'
            elif selvar == 9:
                varname = 'Pot.Temp'
                param = 'THTA'
            elif selvar == 10:
                varname = 'Equiv.Pot.Temp'
                param = 'THTE'
            elif selvar == 11:
                varname = 'Virt.Pot.Temp'
                param = 'THTV'
            else:
                pass

            data = data.append(pd.DataFrame({'Parameter': [varname], 'Pressure': df['PRES'].astype(float)}))
        except:
            pass

    data = data.append(pd.DataFrame({'Parameter': [varname], 'Pressure': df['PRES'].astype(float)}))

    chart = alt.Chart(data).mark_circle().encode(
        x=alt.X('Parameter:N', title='Parameter'),
        y=alt.Y('Pressure:Q', title='Pressure (hPa)', scale=alt.Scale(zero=False)),
        color=alt.Color('Parameter:N', legend=None)
    ).properties(
        width=600,
        height=400
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    st.altair_chart(chart, use_container_width=True)

# Streamlit app
st.title('Vertical Profile Plotter')
st.write('Select parameters and date range to plot the vertical profile.')

# Parameter selection
selvar = st.selectbox('Choose parameter name:',
                      ['Temperature', 'Dewpoint', 'Frost Point', 'RH', 'RH respect to Ice', 'Mixing Ratio',
                       'Wind Direction', 'Wind Speed', 'Pot.Temp', 'Equiv.Pot.Temp', 'Virt.Pot.Temp'])

param_dict = {'Temperature': 1, 'Dewpoint': 2, 'Frost Point': 3, 'RH': 4, 'RH respect to Ice': 5,
              'Mixing Ratio': 6, 'Wind Direction': 7, 'Wind Speed': 8, 'Pot.Temp': 9, 'Equiv.Pot.Temp': 10,
              'Virt.Pot.Temp': 11}

selvar_index = param_dict[selvar]

# Date range selection
start_date = st.date_input("Start date", datetime.date(2024, 1, 1))
end_date = st.date_input("End date", datetime.date(2024, 1, 7))

if st.button('Plot'):
    plot_data(selvar_index, start_date.year, start_date.month, start_date.day)
