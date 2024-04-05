import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

def filter_data_by_year(file_content, target_year):
    lines = file_content.split('\n')
    filtered_data = []
    is_target_year = False
    for line in lines:
        if target_year in line:
            is_target_year = True
        elif 'Observations at' in line:
            is_target_year = False
        if is_target_year:
            filtered_data.append(line)
    return filtered_data
    
def avemaker(file_content, target_year):
    filtered_data = filter_data_by_year(file_content, target_year)
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
def plot_data(selvar, startdate, enddate):
    casedate_list = []
    while startdate <= enddate:
        casedate_list.append(startdate)
        startdate += datetime.timedelta(days=1)

    casedatelist = [n.strftime('%HZ %d %b %Y') for n in casedate_list]
    caseyearlist = [n.strftime('%Y') for n in casedate_list]
    
    datelist1 = [(casedate_list[0] - datetime.timedelta(days=n)).strftime('%HZ %d %b %Y') for n in range(1,8)]
    datelist2 = [(casedate_list[-1] + datetime.timedelta(days=n)).strftime('%HZ %d %b %Y') for n in range(1,4)]
    datelist = datelist1 + datelist2
    
    yearlist1 = [(casedate_list[0] - datetime.timedelta(days=n)).strftime('%Y') for n in range(1,8)]
    yearlist2 = [(casedate_list[-1] + datetime.timedelta(days=n)).strftime('%Y') for n in range(1,4)]
    yearlist = yearlist1 + yearlist2

    fig, ax = plt.subplots(figsize=(6, 8))
    xmin, xmax = 0, 0
    
    url_clim = 'https://raw.githubusercontent.com/alfuadi/sajiva/main/ClimSounding.csv'
    clim = pd.read_csv(url_clim)
    
    for yy, dateofdata, cols, tlag in zip(yearlist, datelist,
                                          ['#65018c', '#0a04b5', '#0546fa', '#0273e3', '#02ced1', '#05f293', '#3ee302',
                                           '#fafa02', '#e6c005', '#fcaa05', '#e37302', '#ff5703', '#e62102', '#f7027d'],
                                          ['-1', '-2', '-3', '-4', '-5', '-6', '-7', '+1', '+2', '+3']):
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

            ax.plot(df[param].astype(float), df['PRES'].astype(float), color=cols, linewidth=2, label=f'D{tlag}', zorder=3)
            ##ax.fill_betweenx(df['PRES'].astype(float), df[param].astype(float), color=cols, alpha=0.3)
            if xmin > df[param].astype(float).min():
                xmin = xmin
            else:
                xmin = df[param].astype(float).min()
            if xmax < df[param].astype(float).max():
                xmax = xmax
            else:
                xmax = df[param].astype(float).max()
            print(dateofdata)
        except:
            pass
    
    for y0, casedate,ndc in zip(caseyearlist, casedatelist, range(len(casedatelist))):
        try:
            url0 = f'https://raw.githubusercontent.com/alfuadi/sajiva/main/nffn/nffn_{y0}.out'
            file_content = requests.get(url0).text
            df = dataframemaker(file_content, casedate)
            ax.plot(df[param].astype(float), df['PRES'].astype(float), color='k', linewidth=2, label=f'Case D({ndc})', zorder=20)            
        except:
            pass
    ##ax.plot(clim[param].astype(float), clim['PRES'].astype(float), alpha=0.5, color='gray', marker='o', linestyle='dashed', linewidth=1, markersize=2, label=f'Clim', zorder=1)
    dave = avemaker(file_content, str(ref_year))
    dave = dave.groupby('PRES').mean()
    st.write(dave)
    ax.plot(dave[param].astype(float), dave['PRES'].astype(float), alpha=0.5, color='gray', marker='o', linestyle='dashed', linewidth=1, markersize=2, label=f'Ave', zorder=21)
    plt.xlabel(varname)
    plt.ylabel('Pressure (hPa)')
    plt.title(f'Vertical Profile of {varname}')
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.yticks([1000, 925, 800, 700, 600, 500, 400, 300, 250, 200, 100])
    plt.legend()
    plt.tight_layout()
    st.pyplot(fig)

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
col1, col2 = st.columns(2)

# Input start date of TC
with col1:
    start_year = st.number_input("Start year", value=1992, min_value=1992)
    start_month = st.number_input("Start month", value=1, min_value=1, max_value=12)
    start_day = st.number_input("Start day", value=1, min_value=1, max_value=31)

# Input end date of TC
with col2:
    end_year = st.number_input("End year", value=datetime.datetime.now().year, min_value=1992)
    end_month = st.number_input("End month", value=datetime.datetime.now().month, min_value=1, max_value=12)
    end_day = st.number_input("End day", value=datetime.datetime.now().day, min_value=1, max_value=31)

# Input comparative year
ref_year = st.number_input("Comparative year", value=datetime.datetime.now().year, min_value=1992)

start_date = datetime.date(start_year, start_month, start_day)
end_date = datetime.date(end_year,end_month,end_day)

if st.button('Plot'):
    print('=======================================')
    plot_data(selvar_index, start_date, end_date)
