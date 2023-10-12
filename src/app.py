# Using Polynomial Regression to Predict Animal Populations

import os
import sys

from outlierFinders import *
sys.path.append('../../src')
from sklearn.linear_model import LinearRegression
import API_helpers.fao as fao
import API_helpers.woah as woah
import API_helpers.helperFunctions
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objects as go
import API_helpers.helperFunctions as helperFunctions
import plotly.figure_factory as ff
from flask import Flask, redirect

# Get app base URL
BASE_URL = os.getenv('BASE_URL','')

countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species   = ["Cattle", "Sheep", "Goats", "Pigs", "Chickens"]
sources   = ['No Options Available']

#Build a Plotly graph around the data
app = Dash(__name__, requests_pathname_prefix=BASE_URL+'/')
app.config["suppress_callback_exceptions"] = True
app.title = "GBADs Informatics User Vizualizer"

app.layout = html.Div(children=[
    dcc.Tabs(id="tabs", value='genDataViewer', children=[
        dcc.Tab(label='General Data View', value='genDataViewer'),
        dcc.Tab(label='Polynomial Regression', value='polyRegress'),
        dcc.Tab(label='Five-Year Population Avg.', value='fiveYearAvg'),
        dcc.Tab(label='Growth Rates', value='growthRates'),
        dcc.Tab(label='IQR', value='iqr'),
    ]),
    html.Div(id='contents'),

    html.H3(children='Countries'),
    dcc.Dropdown(
        countries,
        value=countries[0],
        id="country_checklist",
    ),

    html.H3(children='Species'),
    dcc.Dropdown(
        options=species,
        value=species[0],
        id="species_checklist",
    ),

    html.Br(),
])

#Regular Functions
#5 year avg
def groupBy5Years(data, startYear, endYear, type):
    # Group the data into 5 year intervals
    sum = 0
    counter = 0
    for year in range(int(startYear), int(endYear)):
        try:
            if type == "String":
                row = data[data['year'] == year]
            else:
                row = data[data['year'] == year]

            sum += int(row['population'])
            counter += 1

        except:
            continue

    if counter == 0:
        return 0
    return sum/counter


@app.callback(
        Output('contents', 'children'),
        Input('tabs', 'value'))
def render_content(tab):

    if tab == 'polyRegress':
        return html.Div([
            html.H1(children='Data Quality Comparison for FAOSTAT, WOAH, Census Data, and National Sources using Polynomial Regression'),

            dcc.Graph(id='polyRegressGraph'),

            html.H3(children='Source for Prediction'),
            dcc.Dropdown(
                sources,
                value=sources[0],
                id="sources_checklist",
            ),

            html.Div([
                html.Div([
                    html.H3(children='Degree of Polynomial Regression (>1)'),
                    dcc.Input(id='polyDegree', value='2', type='number'),
                ],style={'width': '49%', 'display': 'inline-block'}),

                html.Div([
                    html.H3(children='Year to be predicted to'),
                dcc.Input(id='maxYear', value='2050', type='number'),
                ],style={'width': '49%', 'display': 'inline-block'}),
            ])
        ])

    elif tab == 'fiveYearAvg':
        return html.Div([
            html.H1(id='fiveYearAvgHeader', children=""),
            dcc.Graph(id='fiveYearAvgGraph'),
            html.H3(children='Some graphs may appear empty due to lack of data'),
        ])

    elif tab == 'genDataViewer':
        return html.Div([
            html.H1(children='Data Quality Comparison for FAOSTAT, WOAH, Census Data, and National Sources'),

            dcc.Graph(id='genDataViewerGraph'),
        ])

    elif tab == 'growthRates':
        specie = "Cattle"
        country = "Ethiopia"
        species = []

        if country == "USA":
            fao_data = fao.get_data("United%20States%20of%20America", specie)
            woah_data = woah.get_data("United%20States%20of%20America", specie)

        elif country == None:
            fao_data = fao.get_data(countries[0], specie)
            woah_data = woah.get_data(countries[0], specie)

        else:
            fao_data = fao.get_data(country, specie)
            woah_data = woah.get_data(country, specie)

        woah_data = woah.formatWoahData(woah_data)
        census_data, csv_index_list, species = API_helpers.helperFunctions.getFormattedCensusData(country, specie)
        national_data, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie)

        # Get the outliers from the FAO Data
        fao_data = helperFunctions.str2frame(fao_data, "faostat")
        fao_data['source'] = "faostat"
        fao_data = fao_data.drop(columns=['iso3', "country"])
        fao_data = fao_data.replace('"','', regex=True)
        fao_data.sort_values(by=['year'], inplace=True)

        # Step two: Get woah data
        if country == "USA":
            woah_data = woah.get_data("United%20States%20of%20America", specie)
        else:
            woah_data = woah.get_data(country, specie)
        woah_data = helperFunctions.str2frame(woah_data, "WOAH")
        woah_data['source'] = "WOAH"
        woah_data = woah_data.drop(columns=['country'])
        woah_data = woah_data.replace('"','', regex=True)
        woah_data.sort_values(by=['year'], inplace=True)

        # Step 3: Get Census data
        try:
            csv_data = pd.read_csv(f"censusData/{country}.csv")
            species = species + csv_data["species"].tolist() # Add the species from the csv file to the list of species
            species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

        except:
            print("Error, count not find the correct csv file")
            csv_data = pd.DataFrame()

        # Step 4: Get National data
        try:
            nationalData = pd.read_csv(f"nationalData/{country}.csv")
            #Add the species from the national data
            species = species + nationalData["species"].tolist() # Add the species from the csv file to the list of species
            species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

        except:
            print("Error, count not find the correct csv file")
            nationalData = pd.DataFrame()

        faoGrowthRate = helperFunctions.growthRate(fao_data, "population", specie)
        faoGrowthRate.sort_values(by=['growthRate'], inplace=True)

        def createGrowthRateFig1(faoGrowthRate):
            if len(faoGrowthRate.index) == 0:
                return html.Div(html.Br())

            data = faoGrowthRate['growthRate'].tolist()

            growthRatesFig1 = ff.create_distplot([data], ["FAOSTAT"], bin_size=0.3, show_rug=False)
            growthRatesFig1.update_xaxes(title_text='Growth Rate')
            growthRatesFig1.update_yaxes(title_text='Density')

            #Add the mean and standard deviation to the graph
            mean = np.mean(data)
            stdev_pluss = np.std(data)
            stdev_minus = np.std(data)*-1
            stdev_pluss2 = np.std(data) * 2
            stdev_minus2 = np.std(data)*-1 * 2
            stdev_pluss3 = np.std(data) * 3
            stdev_minus3 = np.std(data)*-1 * 3


            growthRatesFig1.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'blue', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))

            growthRatesFig1.update_layout(
                font = dict(
                    size=18,
                ),
                plot_bgcolor='white',
            )

            growthRatesFig1.update_yaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            growthRatesFig1.update_xaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            # Get the values outside of the second standard deviation
            fao_outliers = pd.DataFrame(columns=['year', "growthRate"])

            for i in range(len(data)):
                if faoGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or faoGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                    data = [faoGrowthRate.iloc[i]['year'], faoGrowthRate.iloc[i]['growthRate']]
                    row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                    fao_outliers = pd.concat([fao_outliers, row], axis=0)

            return html.Div([
                html.H3(children='FAOSTAT Data for ' + specie + " in " + country, id="growthRatesGraph1Header"),
                dcc.Graph(id='growthRatesGraph1', figure=growthRatesFig1),
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i}
                        for i in fao_outliers.columns],
                    data=fao_outliers.to_dict('records'),
                ),
            ], id="growthRatesGraph1Div")

        #WOAH Data
        woahGrowthRate = helperFunctions.growthRate(woah_data, "population", specie)
        woahGrowthRate.sort_values(by=['growthRate'], inplace=True)

        def createGrowthRateFig2(woahGrowthRate):
            data = woahGrowthRate['growthRate'].tolist()

            growthRatesFig2 = ff.create_distplot([data], ["WOAH"], bin_size=0.3, show_rug=False)
            growthRatesFig2.update_xaxes(title_text='Growth Rate')
            growthRatesFig2.update_yaxes(title_text='Density')

            #Add the mean and standard deviation to the graph
            mean = np.mean(data)
            stdev_pluss = np.std(data)
            stdev_minus = np.std(data)*-1
            stdev_pluss2 = np.std(data) * 2
            stdev_minus2 = np.std(data)*-1 * 2
            stdev_pluss3 = np.std(data) * 3
            stdev_minus3 = np.std(data)*-1 * 3

            growthRatesFig2.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'blue', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))

            growthRatesFig2.update_layout(
                font = dict(
                    size=18,
                ),
                plot_bgcolor='white',
            )

            growthRatesFig2.update_yaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            growthRatesFig2.update_xaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            # Get the values outside of the second standard deviation
            woah_outliers = pd.DataFrame(columns=['year', "growthRate"])

            for i in range(len(data)):
                if woahGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or woahGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                    data = [woahGrowthRate.iloc[i]['year'], woahGrowthRate.iloc[i]['growthRate']]
                    row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                    woah_outliers = pd.concat([woah_outliers, row], axis=0)


            return html.Div([
                html.H3(children='WOAH Data for ' + specie + " in " + country, id="growthRatesGraph2Header"),
                dcc.Graph(id='growthRatesGraph2', figure=growthRatesFig2),
                dash_table.DataTable(
                    id='table2',
                    columns=[{"name": i, "id": i}
                        for i in woah_outliers.columns],
                    data=woah_outliers.to_dict('records'),
                ),
            ], id="growthRatesGraph2Div")

        #Census Data
        censusGrowthRate = helperFunctions.growthRate(census_data, "population", specie)
        censusGrowthRate.sort_values(by=['growthRate'], inplace=True)

        def createGrowthRateFig3(censusGrowthRate):
            data = censusGrowthRate['growthRate'].tolist()
            growthRatesFig3 = None

            if len(data) == 1:
                return html.Div(html.Br())

            else:
                try:
                    growthRatesFig3 = ff.create_distplot([data], ["Census"], bin_size=0.3, show_rug=False)
                    growthRatesFig3.update_xaxes(title_text='Growth Rate')
                    growthRatesFig3.update_yaxes(title_text='Density')

                    #Add the mean and standard deviation to the graph
                    mean = np.mean(data)
                    stdev_pluss = np.std(data)
                    stdev_minus = np.std(data)*-1
                    stdev_pluss2 = np.std(data) * 2
                    stdev_minus2 = np.std(data)*-1 * 2
                    stdev_pluss3 = np.std(data) * 3
                    stdev_minus3 = np.std(data)*-1 * 3

                    growthRatesFig3.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'blue', dash = 'dash'))
                    growthRatesFig3.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'red', dash = 'dash'))
                    growthRatesFig3.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'red', dash = 'dash'))
                    growthRatesFig3.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'black', dash = 'dash'))
                    growthRatesFig3.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'black', dash = 'dash'))
                    growthRatesFig3.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'orange', dash = 'dash'))
                    growthRatesFig3.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'orange', dash = 'dash'))

                    growthRatesFig3.update_layout(
                        font = dict(
                            size=18,
                        ),
                        plot_bgcolor='white',
                    )

                    growthRatesFig3.update_yaxes(
                        type='linear',
                        mirror=True,
                        ticks='outside',
                        showline=True,
                        linecolor='black',
                        gridcolor='lightgrey'
                    )

                    growthRatesFig3.update_xaxes(
                        type='linear',
                        mirror=True,
                        ticks='outside',
                        showline=True,
                        linecolor='black',
                        gridcolor='lightgrey'
                    )

                    # Get the values outside of the second standard deviation
                    for i in range(len(data)):
                        if censusGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or censusGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                            data = [censusGrowthRate.iloc[i]['year'], censusGrowthRate.iloc[i]['growthRate']]
                            row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                            census_outliers = pd.concat([census_outliers, row], axis=0)

                except Exception as e:
                    print("Fig 3 exception. Exception is: ", e)
                    return html.Div(children=[html.Br()], id="growthRatesGraph3Div")

                return html.Div(children = [
                    html.H3(children='Census Data for ' + specie + " in " + country),
                    dcc.Graph(id='growthRatesGraph3', figure=growthRatesFig3),
                    dash_table.DataTable(
                        id='table3',
                        columns=[{"name": i, "id": i}
                            for i in census_outliers.columns],
                        data=census_outliers.to_dict('records'),
                    ),
                ], id="growthRatesGraph3Div")

        #National Data
        NationalGrowthRate = helperFunctions.growthRate(national_data, "population", specie)
        NationalGrowthRate.sort_values(by=['growthRate'], inplace=True)

        def createGrowthRateFig4(NationalGrowthRate):
            data = NationalGrowthRate['growthRate'].tolist()
            growthRatesFig = None

            if len(data) == 1:
                return html.Div(html.Br())
            else:
                try:
                    growthRatesFig = ff.create_distplot([data], ["National"], bin_size=0.3, show_rug=False)
                    growthRatesFig.update_xaxes(title_text='Growth Rate')
                    growthRatesFig.update_yaxes(title_text='Density')

                    #Add the mean and standard deviation to the graph
                    mean = np.mean(data)
                    stdev_pluss = np.std(data)
                    stdev_minus = np.std(data)*-1
                    stdev_pluss2 = np.std(data) * 2
                    stdev_minus2 = np.std(data)*-1 * 2
                    stdev_pluss3 = np.std(data) * 3
                    stdev_minus3 = np.std(data)*-1 * 3

                    growthRatesFig.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'blue', dash = 'dash'))
                    growthRatesFig.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'red', dash = 'dash'))
                    growthRatesFig.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'red', dash = 'dash'))
                    growthRatesFig.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'black', dash = 'dash'))
                    growthRatesFig.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'black', dash = 'dash'))
                    growthRatesFig.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'orange', dash = 'dash'))
                    growthRatesFig.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                                line = dict(color = 'orange', dash = 'dash'))

                    growthRatesFig.update_layout(
                        # title="Distribution of Growth Rates for Census Data for " + specie + " in " + country,
                        font = dict(
                            size=18,
                        ),
                        plot_bgcolor='white',
                    )

                    growthRatesFig.update_yaxes(
                        type='linear',
                        mirror=True,
                        ticks='outside',
                        showline=True,
                        linecolor='black',
                        gridcolor='lightgrey'
                    )

                    growthRatesFig.update_xaxes(
                        type='linear',
                        mirror=True,
                        ticks='outside',
                        showline=True,
                        linecolor='black',
                        gridcolor='lightgrey'
                    )

                    # Get the values outside of the second standard deviation
                    national_outliers = pd.DataFrame(columns=['year', "growthRate"])

                    for i in range(len(data)):
                        if NationalGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or NationalGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                            data = [NationalGrowthRate.iloc[i]['year'], NationalGrowthRate.iloc[i]['growthRate']]
                            row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                            national_outliers = pd.concat([national_outliers, row], axis=0)

                except Exception as e:
                    print("Fig 4 exception. Exception is: ", e)
                    return html.Div(html.Br())

                return html.Div(children = [
                    html.H3(children='National Data for ' + specie + " in " + country),
                    dcc.Graph(id='growthRatesGraph4', figure=growthRatesFig),
                    dash_table.DataTable(
                        id='table3',
                        columns=[{"name": i, "id": i}
                            for i in national_outliers.columns],
                        data=national_outliers.to_dict('records'),
                    ),
                ], id="growthRatesGraph4Div")

        return html.Div([
            createGrowthRateFig1(faoGrowthRate),
            createGrowthRateFig2(woahGrowthRate),
            createGrowthRateFig3(censusGrowthRate),
            createGrowthRateFig4(NationalGrowthRate),
        ])

    elif tab == 'iqr':
        return html.Div([
            html.H1(id='iqrHeader', children=""),
            dcc.Graph(id='iqrGraph'),

            html.H3(children='Year Range'),
            html.Div(children=[
                html.H3(children='Select the range of years you would like to see'),
                dcc.Dropdown(
                    id='startYearDropDown',
                    options=[{'label': i, 'value': i} for i in range(1993, 2019)],
                    value=1993
                ),
                dcc.Dropdown(
                    id='endYearDropDown',
                    options=[{'label': i, 'value': i} for i in range(1961, 2021)],
                    value=2020
                ),
            ],
            style={'width': '49%', 'display': 'inline-block'},
            id = "iqrDataRangeDropDowns"),

            dcc.Checklist(options=['Remove Outliers'], value=[], id="removeOutliers"),
        ])

    else:
        return html.Div()


@app.callback(
    Output("growthRatesGraph1Div", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateGrowthRatesGraph1(specie, country):
    if specie == None:
        specie = species[0]

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)

    elif country == None:
        fao_data = fao.get_data(countries[0], specie)

    else:
        fao_data = fao.get_data(country, specie)

    # Get the outliers from the FAO Data
    fao_data = helperFunctions.str2frame(fao_data, "faostat")
    fao_data['source'] = "faostat"
    fao_data = fao_data.drop(columns=['iso3', "country"])
    fao_data = fao_data.replace('"','', regex=True)
    fao_data.sort_values(by=['year'], inplace=True)

    faoGrowthRate = helperFunctions.growthRate(fao_data, "population", specie)
    faoGrowthRate.sort_values(by=['growthRate'], inplace=True)


    faoGrowthRate = helperFunctions.growthRate(fao_data, "population", specie)
    faoGrowthRate.sort_values(by=['growthRate'], inplace=True)

    data = faoGrowthRate['growthRate'].tolist()

    if len(data) == 0:
        return html.Div(html.Br())

    else:
        try:
            growthRatesFig1 = ff.create_distplot([data], ["FAOSTAT"], bin_size=0.3, show_rug=False)
            growthRatesFig1.update_xaxes(title_text='Growth Rate')
            growthRatesFig1.update_yaxes(title_text='Density')

            #Add the mean and standard deviation to the graph
            mean = np.mean(data)
            stdev_pluss = np.std(data)
            stdev_minus = np.std(data)*-1
            stdev_pluss2 = np.std(data) * 2
            stdev_minus2 = np.std(data)*-1 * 2
            stdev_pluss3 = np.std(data) * 3
            stdev_minus3 = np.std(data)*-1 * 3

            growthRatesFig1.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'blue', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))
            growthRatesFig1.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))

            growthRatesFig1.update_layout(
                font = dict(
                    size=18,
                ),
                plot_bgcolor='white',
            )

            growthRatesFig1.update_yaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            growthRatesFig1.update_xaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            # Get the values outside of the second standard deviation
            fao_outliers = pd.DataFrame(columns=['year', "growthRate"])

            for i in range(len(data)):
                if faoGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or faoGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                    data = [faoGrowthRate.iloc[i]['year'], faoGrowthRate.iloc[i]['growthRate']]
                    row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                    fao_outliers = pd.concat([fao_outliers, row], axis=0)

            return html.Div([
                html.H3(children='FAOSTAT Data for ' + specie + " in " + country, id="growthRatesGraph1Header"),
                dcc.Graph(id='growthRatesGraph1', figure=growthRatesFig1),
                dash_table.DataTable(
                    id='table1',
                    columns=[{"name": i, "id": i}
                        for i in fao_outliers.columns],
                    data=fao_outliers.to_dict('records'),
                ),
            ], id="growthRatesGraph1Div")

        except Exception as e:
            print("Exception is: ", e)
            return html.Div(html.Br())


@app.callback(
    Output("growthRatesGraph1Header", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateGrowthRatesGraph1Header(specie, country):
    return 'FAOSTAT Data for ' + specie + " in " + country


@app.callback(
    Output("growthRatesGraph2Header", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateGrowthRatesGraph1Header(specie, country):
    return 'WOAH Data for ' + specie + " in " + country


@app.callback(
    Output("growthRatesGraph2Div", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateGrowthRatesGraph2(specie, country):
    if specie == None:
        specie = species[0]

    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)

    elif country == None:
        woah_data = woah.get_data(countries[0], specie)

    else:
        woah_data = woah.get_data(country, specie)

    woah_data = woah.formatWoahData(woah_data)
    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        woah_data = woah.get_data(country, specie)
    woah_data = helperFunctions.str2frame(woah_data, "WOAH")
    woah_data['source'] = "WOAH"
    woah_data = woah_data.drop(columns=['country'])
    woah_data = woah_data.replace('"','', regex=True)
    woah_data.sort_values(by=['year'], inplace=True)

    woahGrowthRate = helperFunctions.growthRate(woah_data, "population", specie)
    woahGrowthRate.sort_values(by=['growthRate'], inplace=True)

    data = woahGrowthRate['growthRate'].tolist()

    if len(data) == 0:
        return html.Div(html.Br())

    else:
        try:

            growthRatesFig2 = ff.create_distplot([data], ["WOAH"], bin_size=0.3, show_rug=False)
            growthRatesFig2.update_xaxes(title_text='Growth Rate')
            growthRatesFig2.update_yaxes(title_text='Density')

            #Add the mean and standard deviation to the graph
            mean = np.mean(data)
            stdev_pluss = np.std(data)
            stdev_minus = np.std(data)*-1
            stdev_pluss2 = np.std(data) * 2
            stdev_minus2 = np.std(data)*-1 * 2
            stdev_pluss3 = np.std(data) * 3
            stdev_minus3 = np.std(data)*-1 * 3

            growthRatesFig2.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'blue', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'Black', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))
            growthRatesFig2.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))

            growthRatesFig2.update_layout(        font = dict(
                    size=18,
                ),
                plot_bgcolor='white',
            )

            growthRatesFig2.update_yaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            growthRatesFig2.update_xaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            woah_outliers = pd.DataFrame(columns=['year', "growthRate"])

            for i in range(len(data)):
                if woahGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or woahGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                    data = [woahGrowthRate.iloc[i]['year'], woahGrowthRate.iloc[i]['growthRate']]
                    row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                    woah_outliers = pd.concat([woah_outliers, row], axis=0)

            return html.Div([
                html.H3(children='WOAH Data for ' + specie + " in " + country, id="growthRatesGraph2Header"),
                dcc.Graph(id='growthRatesGraph2', figure=growthRatesFig2),
                dash_table.DataTable(
                    id='table2',
                    columns=[{"name": i, "id": i}
                        for i in woah_outliers.columns],
                    data=woah_outliers.to_dict('records'),
                ),
            ], id="growthRatesGraph2Div")

        except Exception as e:
            print("Exception is: ", e)
            return html.Div(html.Br())


@app.callback(
    Output("growthRatesGraph3Div", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateGrowthRatesGraph3(specie, country):
    census_data, csv_index_list, species = API_helpers.helperFunctions.getFormattedCensusData(country, specie)
    censusGrowthRate = helperFunctions.growthRate(census_data, "population", specie)
    censusGrowthRate.sort_values(by=['growthRate'], inplace=True)

    data = censusGrowthRate['growthRate'].tolist()

    if len(data) == 1:
        return html.Br()

    else:
        try:
            census_outliers = pd.DataFrame(columns=['year', "growthRate"])

            growthRatesFig3 = ff.create_distplot([data], ["Census"], bin_size=0.3, show_rug=False)
            growthRatesFig3.update_xaxes(title_text='Growth Rate')
            growthRatesFig3.update_yaxes(title_text='Density')

            #Add the mean and standard deviation to the graph
            mean = np.mean(data)
            stdev_pluss = np.std(data)
            stdev_minus = np.std(data)*-1
            stdev_pluss2 = np.std(data) * 2
            stdev_minus2 = np.std(data)*-1 * 2
            stdev_pluss3 = np.std(data) * 3
            stdev_minus3 = np.std(data)*-1 * 3


            growthRatesFig3.add_shape(type="line", x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'blue', dash = 'dash'))
            growthRatesFig3.add_shape(type="line", x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig3.add_shape(type="line", x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig3.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'black', dash = 'dash'))
            growthRatesFig3.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'black', dash = 'dash'))
            growthRatesFig3.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))
            growthRatesFig3.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))

            growthRatesFig3.update_layout(
                font = dict(
                    size=18,
                ),
                plot_bgcolor='white',
            )

            growthRatesFig3.update_yaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            growthRatesFig3.update_xaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            # Get the values outside of the second standard deviation
            census_outliers = pd.DataFrame(columns=['year', "growthRate"])

            for i in range(len(data)):
                if censusGrowthRate.iloc[i]['growthRate'] > stdev_pluss * 3 or censusGrowthRate.iloc[i]['growthRate'] < stdev_minus * 3:
                    data = [censusGrowthRate.iloc[i]['year'], censusGrowthRate.iloc[i]['growthRate']]
                    row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                    census_outliers = pd.concat([census_outliers, row], axis=0)

            return [
                html.H3(children='Census Data for ' + specie + " in " + country),
                dcc.Graph(id='growthRatesGraph3', figure=growthRatesFig3),
                dash_table.DataTable(
                    id='table3',
                    columns=[{"name": i, "id": i}
                        for i in census_outliers.columns],
                    data=census_outliers.to_dict('records'),
                ),
            ]
        except:
            return html.Br()


@app.callback(
    Output("growthRatesGraph4Div", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateGrowthRatesGraph4(specie, country):
    national_data, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie)
    NationalGrowthRate = helperFunctions.growthRate(national_data, "population", specie)
    NationalGrowthRate.sort_values(by=['growthRate'], inplace=True)

    data = NationalGrowthRate['growthRate'].tolist()
    growthRatesFig = None

    if len(data) == 1:
        return html.Br()

    else:
        try:
            growthRatesFig = ff.create_distplot([data], ["National"], bin_size=0.3, show_rug=False)
            growthRatesFig.update_xaxes(title_text='Growth Rate')
            growthRatesFig.update_yaxes(title_text='Density')

            # Add the mean and standard deviation to the graph
            mean = np.mean(data)
            stdev_pluss = np.std(data)
            stdev_minus = np.std(data)*-1
            stdev_pluss2 = np.std(data) * 2
            stdev_minus2 = np.std(data)*-1 * 2
            stdev_pluss3 = np.std(data) * 3
            stdev_minus3 = np.std(data)*-1 * 3

            growthRatesFig.add_shape(type="line",x0=mean, x1=mean, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'blue', dash = 'dash'))
            growthRatesFig.add_shape(type="line",x0=stdev_pluss, x1=stdev_pluss, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig.add_shape(type="line",x0=stdev_minus, x1=stdev_minus, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'red', dash = 'dash'))
            growthRatesFig.add_shape(type="line",x0=stdev_pluss2, x1=stdev_pluss2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'black', dash = 'dash'))
            growthRatesFig.add_shape(type="line",x0=stdev_minus2, x1=stdev_minus2, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'black', dash = 'dash'))
            growthRatesFig.add_shape(type="line",x0=stdev_pluss3, x1=stdev_pluss3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))
            growthRatesFig.add_shape(type="line",x0=stdev_minus3, x1=stdev_minus3, y0 =0, y1=0.4 , xref='x', yref='y',
                        line = dict(color = 'orange', dash = 'dash'))

            growthRatesFig.update_layout(
                font = dict(
                    size=18,
                ),
                plot_bgcolor='white',
            )

            growthRatesFig.update_yaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            growthRatesFig.update_xaxes(
                type='linear',
                mirror=True,
                ticks='outside',
                showline=True,
                linecolor='black',
                gridcolor='lightgrey'
            )

            national_outliers = pd.DataFrame(columns=['year', "growthRate"])
            for i in range(len(data)):
                if growthRatesFig.iloc[i]['growthRate'] > stdev_pluss * 3 or growthRatesFig.iloc[i]['growthRate'] < stdev_minus * 3:
                    data = [growthRatesFig.iloc[i]['year'], growthRatesFig.iloc[i]['growthRate']]
                    row = round(pd.DataFrame([data], columns=['year', "growthRate"]), 2)
                    national_outliers = pd.concat([growthRatesFig, row], axis=0)


            return [
                html.H3(children='National Data for ' + specie + " in " + country),
                dcc.Graph(id='growthRatesGraph4', figure=growthRatesFig),
                dash_table.DataTable(
                    id='table3',
                    columns=[{"name": i, "id": i}
                        for i in national_outliers.columns],
                    data=national_outliers.to_dict('records'),
                ),
            ]

        except Exception as e:
            return html.Br()


@app.callback(
    Output("iqrDataRangeDropDowns", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateStartAndEndYearDropDowns(specie, country):

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        fao_data = fao.get_data(country, specie)
        woah_data = woah.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)
    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census Data
    csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie)

    #Only get the rows that have the correct specie
    new_csv_data = []
    for index, row in csv_data.iterrows():
        if row['species'] == specie:
            new_csv_data.append( [row['year'], row['population']] )

    csv_data = pd.DataFrame(new_csv_data, columns = ["year", "population"])

    # Step 4: Get National Data
    nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie)

    new_national_data = []
    for index, row in nationalData.iterrows():
        if row['species'] == specie:
            new_national_data.append( [row['year'], row['population']] )

    nationalData = pd.DataFrame (new_national_data, columns = ["year", "population"])

    def findLowestYear(df):
        years = df.year.unique()
        years.sort()
        if years.size == 0:
            return 2021, 1959
        elif years.size == 1:
            return years[0], years[0]

        else:
            return years[0], years[-1]

    lowestYear, greatestYear = findLowestYear(fao_data)
    woahLowestYear, woahGreatestYear = findLowestYear(woah_data)

    if woahLowestYear < lowestYear:
        lowestYear = woahLowestYear

    if woahGreatestYear > greatestYear:
        greatestYear = woahGreatestYear

    csvLowestYear, csvGreatestYear = findLowestYear(csv_data)

    if csvLowestYear < lowestYear:
        lowestYear = csvLowestYear

    if csvGreatestYear > greatestYear:
        greatestYear = csvGreatestYear

    nationalLowestYear, nationalDataGreatestYear = findLowestYear(nationalData)

    if nationalLowestYear < lowestYear:
        lowestYear = nationalLowestYear

    if nationalDataGreatestYear > greatestYear:
        greatestYear = nationalDataGreatestYear

    return html.Div([
        html.H3(children='Select the range of years you would like to see'),
        dcc.Dropdown(
            id='startYearDropDown',
            options=[{'label': i, 'value': i} for i in range(lowestYear, greatestYear + 1)],
            value=lowestYear
        ),
        dcc.Dropdown(
            id='endYearDropDown',
            options=[{'label': i, 'value': i} for i in range(lowestYear, greatestYear + 1)],
            value=greatestYear
        ),
    ])


@app.callback(
    Output("endYearDropDown", "value"),
    Input("startYearDropDown", "value"),
    Input("endYearDropDown", "value"))
def updateEndYearDropDown(startYear, endYear):
    if startYear == None or endYear == None:
        return None

    elif startYear >= endYear:
        return 2019

    else:
        return endYear


@app.callback(
    Output("iqrHeader", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def createIqrHeader(specie, country):
    return f'IQR of Rate of Change of Population for ' + specie + " in " + country

@app.callback(
    Output("iqrGraph", "figure"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"),
    Input("startYearDropDown", "value"),
    Input("endYearDropDown", "value"),
    Input("removeOutliers", "value"))
def createIqrGraph(specie, country, startYear, endYear, removeOutliers):

    if startYear == None or endYear == None:
        masterDf = pd.DataFrame(columns=['Source', "rateOfChange"])
        return px.box( masterDf, y="rateOfChange", x="Source", points="all")

    startYear = int(startYear)
    endYear = int(endYear)

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        fao_data = fao.get_data(country, specie)
        woah_data = woah.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)
    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census Data
    csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie)

    #Only get the rows that have the correct specie
    new_csv_data = []
    for index, row in csv_data.iterrows():
        if row['species'] == specie:
            new_csv_data.append( [row['year'], row['population']] )

    csv_data = pd.DataFrame(new_csv_data, columns = ["year", "population"])

    # Step 4: Get National Data
    nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie)

    new_national_data = []
    for index, row in nationalData.iterrows():
        if row['species'] == specie:
            new_national_data.append( [row['year'], row['population']] )

    nationalData = pd.DataFrame (new_national_data, columns = ["year", "population"])

    # Get the rate of change of each point in each data set and put it into arrays
    fao_roc = helperFunctions.getROC(fao_data, "population")
    woah_roc = helperFunctions.getROC(woah_data, "population")
    csv_roc = helperFunctions.getROC(csv_data, "population")
    national_roc = helperFunctions.getROC(nationalData, "population")

    #Get the IQR for FAO
    fao_data = fao_roc.values.tolist()
    fao_dict = {}

    for elem in fao_data:
        fao_dict[int(elem[0])] = elem[1] #elem[0] = year, elem[1] = value

    fao_iqr_list = []
    counter = 0
    for i in range(startYear, endYear):
        counter += 1
        #Add all the years that exist in the range
        try:
            fao_iqr_list.append(float(fao_dict[i]))
        except:
            continue

    fao_iqr_list.sort()

    try:
        firstHalf = fao_iqr_list[:len(fao_iqr_list)//2]
        secondHalf = fao_iqr_list[len(fao_iqr_list)//2:]

        firstQuartile = firstHalf[:len(firstHalf)//2]
        thirdQuartile = secondHalf[:len(secondHalf)//2]
    except:
        firstHalf = []
        secondHalf = []
        firstQuartile = []
        thirdQuartile = []


    fao_q1 = np.percentile(fao_iqr_list, 25)
    fao_q3 = np.percentile(fao_iqr_list, 75)

    fao_iqr = 0

    if firstQuartile != [] and thirdQuartile != []:
        fao_iqr = fao_q3 - fao_q1

    #Get the IQR for woah
    woah_data = woah_roc.values.tolist()
    woah_dict = {}

    for elem in woah_data:
        woah_dict[int(elem[0])] = elem[1]

    woah_iqr_list = []
    for i in range(startYear, endYear):
        try:
            woah_iqr_list.append(woah_dict[i])
        except:
            continue

    woah_iqr_list.sort()

    try:
        firstHalf = woah_iqr_list[:len(woah_iqr_list)//2]
        secondHalf = woah_iqr_list[len(woah_iqr_list)//2:]

        firstQuartile = firstHalf[:len(firstHalf)//2]
        thirdQuartile = secondHalf[:len(secondHalf)//2]
    except:
        firstHalf = []
        secondHalf = []
        firstQuartile = []
        thirdQuartile = []

    woah_iqr = 0
    woah_q1 = 0
    woah_q3 = 0

    if firstQuartile != [] and thirdQuartile != []:
        woah_q1 = np.percentile(woah_iqr_list, 25)
        woah_q3 = np.percentile(woah_iqr_list, 75)
        woah_iqr = woah_q3 - woah_q1

    #Get the IQR for CSV
    csv_data = csv_roc.values.tolist()
    csv_dict = {}

    for elem in csv_data:
        csv_dict[int(elem[0])] = elem[1]

    csv_iqr_list = []
    for i in range(startYear, endYear):
        #Add all the years that exist in the range
        try:
            csv_iqr_list.append(csv_dict[i])
        except:
            continue

    try:
        firstHalf = csv_iqr_list[:len(csv_iqr_list)//2]
        secondHalf = csv_iqr_list[len(csv_iqr_list)//2:]

        firstQuartile = firstHalf[:len(firstHalf)//2]
        thirdQuartile = secondHalf[:len(secondHalf)//2]
    except:
        firstHalf = []
        secondHalf = []
        firstQuartile = []
        thirdQuartile = []

    csv_iqr = -1
    csv_q1 = 0
    csv_q3 = 0

    if firstQuartile != [] and thirdQuartile != []:
        csv_q1 = np.percentile(firstQuartile, 25)
        csv_q3 = np.percentile(thirdQuartile, 75)
        csv_iqr = csv_q3 - csv_q1


    #Get the IQR for National
    national_data = national_roc.values.tolist()
    national_dict = {}

    for elem in national_data:
        national_dict[int(elem[0])] = elem[1]

    national_iqr_list = []
    for i in range(startYear, endYear):
        #Add all the years that exist in the range
        try:
            national_iqr_list.append(national_dict[i])
        except:
            continue

    try:
        firstHalf = national_iqr_list[:len(national_iqr_list)//2]
        secondHalf = national_iqr_list[len(national_iqr_list)//2:]

        firstQuartile = firstHalf[:len(firstHalf)//2]
        thirdQuartile = secondHalf[:len(secondHalf)//2]
    except:
        firstHalf = []
        secondHalf = []
        firstQuartile = []
        thirdQuartile = []

    national_q1 = 0
    national_q3 = 0
    national_iqr = -1

    if firstQuartile != [] and thirdQuartile != []:
        national_q1 = np.percentile(firstQuartile, 25)
        national_q3 = np.percentile(thirdQuartile, 75)
        national_iqr = national_q3 - national_q1


    #Get the upper and lower fence
    fao_upperFence = fao_q3 + (1.5 * fao_iqr)
    fao_lowerFence = fao_q1 - (1.5 * fao_iqr)

    woah_upperFence = woah_q3 + (1.5 * woah_iqr)
    woah_lowerFence = woah_q1 - (1.5 * woah_iqr)

    if csv_iqr != -1:
        csv_upperFence = csv_q3 + (1.5 * csv_iqr)
        csv_lowerFence = csv_q1 - (1.5 * csv_iqr)

    if national_iqr != -1:
        national_upperFence = national_q3 + (1.5 * national_iqr)
        national_lowerFence = national_q1 - (1.5 * national_iqr)

    newDf = pd.DataFrame(columns=['year', 'rateOfChange'])
    for i in range(woah_roc.shape[0]):
        newDf.loc[i] = woah_roc.iloc[i]

    woah_roc = newDf

    # Remove the outliers?
    if removeOutliers != []:

        #Remove the outliers from fao
        index = 0
        for elem in fao_iqr_list:
            if elem > fao_upperFence or elem < fao_lowerFence:
                fao_iqr_list.pop(index)

            index += 1

        #Remove the outliers from woah
        index = 0
        for elem in woah_iqr_list:
            if elem > woah_upperFence or elem < woah_lowerFence:
                woah_iqr_list.pop(index)
            index += 1

        #Remove the outliers from csv
        if csv_iqr != -1:
            index = 0
            for elem in csv_iqr_list:
                if elem > csv_upperFence or elem < csv_lowerFence:
                    csv_iqr_list.pop(index)
                index += 1

        #Remove the outliers from national
        if national_iqr != -1:
            index = 0
            for elem in national_iqr_list:
                if elem > national_upperFence or elem < national_lowerFence:
                    national_iqr_list.pop(index)
                index += 1

    #Fao
    faoCopy = pd.DataFrame(columns=['rateOfChange'])
    faoCopy['rateOfChange']= fao_iqr_list
    faoNewCol = ['FAOSTAT' for i in range(len(faoCopy))]
    faoCopy['Source'] = faoNewCol

    masterDf = faoCopy

    #woah
    woahCopy = pd.DataFrame(columns=['rateOfChange'])
    woahCopy['rateOfChange']= woah_iqr_list
    woahNewCol = ['WOAH' for i in range(len(woahCopy))]
    woahCopy['Source'] = woahNewCol

    masterDf = pd.concat([masterDf, woahCopy])

    #csv
    csvCopy = pd.DataFrame(columns=['rateOfChange'])
    csvCopy['rateOfChange']= csv_iqr_list
    csvNewCol = ['UN Census Data' for i in range(len(csvCopy))]
    csvCopy['Source'] = csvNewCol

    masterDf = pd.concat([masterDf, csvCopy])

    #National
    nationalCopy = pd.DataFrame(columns=['rateOfChange'])
    nationalCopy['rateOfChange']= national_iqr_list
    nationalNewCol = ['National Census Bureau' for i in range(len(nationalCopy))]
    nationalCopy['Source'] = nationalNewCol

    masterDf = pd.concat([masterDf, nationalCopy])

    fig = px.box( masterDf, y="rateOfChange", x="Source", points="all")

    fig.update_layout(
        title=f"IQR of Rate of Change of Population for {specie} in {country}",
        font= dict(
            size = 18,
            color = "black"
        ),
        xaxis_title="Source",
        yaxis_title="Rate of Change",
        legend_title="Source",
        plot_bgcolor='white',
    )

    fig.update_yaxes(
        type='linear',
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    return fig


@app.callback(
    Output("fiveYearAvgGraph", "figure"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def createFiveYearAvgGraph(specie, country):

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        fao_data = fao.get_data(country, specie)
        woah_data = woah.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)
    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census Data
    csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie)

    # Only get the rows that have the correct specie
    new_csv_data = []
    for index, row in csv_data.iterrows():
        if row['species'] == specie:
            new_csv_data.append( [row['year'], row['population']] )

    csv_data = pd.DataFrame(new_csv_data, columns = ["year", "population"])

    # Step 4: Get National Data
    nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie)

    new_national_data = []
    for index, row in nationalData.iterrows():
        if row['species'] == specie:
            new_national_data.append( [row['year'], row['population']] )

    nationalData = pd.DataFrame (new_national_data, columns = ["year", "population"])

    #Get a list of all the years from each data source
    fao_years = fao_data['year'].tolist()
    woah_years = woah_data['year'].tolist()
    csv_years = csv_data['year'].tolist()
    national_years = nationalData['year'].tolist()

    #Combine the years into a set and sort them
    years = fao_years + woah_years + csv_years + national_years
    years = list(dict.fromkeys(years))
    years = [int(s) for s in years]
    years.sort()

    #Get each ones five year averages
    fao_averages = []
    woah_averages = []
    csv_averages = []
    national_averages = []
    yearsArr = []

    if len(years) == 0:
        print("No data found")
        exit()

    counter = 0
    for i in range(years[0], years[-1]):
        if counter % 5 == 0 and counter != 0:
            fao_averages.append(groupBy5Years(fao_data, i - 5, i, "String"))
            woah_averages.append(groupBy5Years(woah_data, i - 5, i, "String"))
            csv_averages.append(groupBy5Years(csv_data, i - 5, i, "Int"))
            national_averages.append(groupBy5Years(nationalData, i - 5, i, "Int"))
            yearsArr.append(i)

        counter += 1

    #Find the percent changes
    fao_percent_change = []
    woah_percent_change = []
    csv_percent_change = []
    national_percent_change = []
    if len(yearsArr) > 0:
        yearsArr.pop(0)

    for i in range(1, len(fao_averages)):
        if fao_averages[i-1] == 0 or fao_averages[i] == 0:
            fao_percent_change.append(0)
        else:
            fao_percent_change.append( ((fao_averages[i] - fao_averages[i-1]) / fao_averages[i-1]) * 100 )

        if woah_averages[i-1] == 0 or woah_averages[i] == 0:
            woah_percent_change.append(0)
        else:
            woah_percent_change.append( ((woah_averages[i] - woah_averages[i-1]) / woah_averages[i-1]) * 100 )

        if csv_averages[i-1] == 0 or csv_averages[i] == 0:
            csv_percent_change.append(0)
        else:
            csv_percent_change.append( ((csv_averages[i] - csv_averages[i-1]) / csv_averages[i-1]) * 100 )

        if national_averages[i-1] == 0 or national_averages[i] == 0:
            national_percent_change.append(0)
        else:
            national_percent_change.append( ((national_averages[i] - national_averages[i-1]) / national_averages[i-1]) * 100 )

    #Graph them
    calculateFiveYearAvgOutliersInternal(fao_percent_change, woah_percent_change, csv_percent_change, national_percent_change, yearsArr, specie, country)
    calculateFiveYearAvgOutliersExternal(fao_percent_change, woah_percent_change, csv_percent_change, national_percent_change, yearsArr, specie, country)


    masterDf = pd.DataFrame(columns = ["year", "faostat", "WOAH", "census", "national",])
    masterDf['FAOSTAT'] = fao_percent_change
    masterDf['WOAH'] = woah_percent_change
    masterDf['census'] = csv_percent_change
    masterDf['national'] = national_percent_change
    masterDf['year'] = yearsArr

    # Census and national are all zeros
    if masterDf['census'].isnull().values.any() and masterDf['national'].isnull().values.any():

        fig = go.Figure([
            go.Bar(name='FAOSTAT', x=masterDf['year'], y=masterDf['FAOSTAT']),
            go.Bar(name='WOAH', x=masterDf['year'], y=masterDf['WOAH'])
        ])

    #National is all zeros
    elif masterDf['national'].isnull().values.any():
        fig = go.Figure([
            go.Bar(name='FAOSTAT', x=masterDf['year'], y=masterDf['FAOSTAT']),
            go.Bar(name='National', x=masterDf['year'], y=masterDf['national']),
            go.Bar(name='WOAH', x=masterDf['year'], y=masterDf['WOAH']),
        ])

    #Census is all zeros
    elif masterDf['census'].isnull().values.any():
        fig = go.Figure([
            go.Bar(name='FAOSTAT', x=masterDf['year'], y=masterDf['FAOSTAT']),
            go.Bar(name='Census', x=masterDf['year'], y=masterDf['census']),
            go.Bar(name='WOAH', x=masterDf['year'], y=masterDf['WOAH']),
        ])

    else:
        fig = go.Figure([
            go.Bar(name='FAOSTAT', x=masterDf['year'], y=masterDf['FAOSTAT']),
            go.Bar(name='Census', x=masterDf['year'], y=masterDf['census']),
            go.Bar(name='National', x=masterDf['year'], y=masterDf['national']),
            go.Bar(name='WOAH', x=masterDf['year'], y=masterDf['WOAH']),
        ])

    fig.update_layout(
        xaxis = dict(
            tickmode='array',
            tickvals = yearsArr,
            ticktext = yearsArr,
        ),
        font=dict(
            color="black",
            size=18
        ),
        plot_bgcolor='white',
    )

    fig.update_yaxes(
        type='linear',
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title="Percent Change"
    )

    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title="Year",
        nticks=len(yearsArr)
    )

    return fig


@app.callback(
    Output("fiveYearAvgHeader", "children"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def updateFiveYearAvgHeader(specie, country):
    return 'Five Year Average of Rate of Change of Population for ' + specie + " in " + country


@app.callback(
    Output("species_checklist", "options"),
    Input("country_checklist", "value"))
def update_species_checklist(country):

    try:
        csv_data = pd.read_csv(f"censusData/{country}.csv")
        species = csv_data["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

    except:
        print("Error, count not find the correct csv file")

    try:
        nationalData = pd.read_csv(f"nationalData/{country}.csv")
        species = nationalData["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species

    except:
        print("Error, count not find the correct csv file")

    return species


@app.callback(
    Output("sources_checklist", "options"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def populate_dropDown(specie, country):

    if specie == None:
        if species == None or species == []:
            specie = "Cattle"
        else:
            specie = species[0]

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)

    elif country == None:
        fao_data = fao.get_data("Ethiopia", specie)

    else:
        fao_data = fao.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)

    # Step two: Get woah data
    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        woah_data = woah.get_data(country, specie)

    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census data
    csv_data, csv_index_list, species  = API_helpers.helperFunctions.getFormattedCensusData(country, specie)

    # Step 4: Get National data
    nationalData, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie)

    #Fill the dropdown with the available sources
    sources = []
    if fao_data.empty == False:
        sources.append("FAOSTAT")

    if woah_data.empty == False:
        sources.append("WOAH")

    if csv_data.empty == False:
        sources.append("UN Census Data")

    if nationalData.empty == False:
        sources.append("National Census Data")

    if sources == []:
        sources = ["No Options Available"]

    return sources


@app.callback(
    Output("polyRegressGraph", "figure"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"),
    Input("sources_checklist", "value"),
    Input("polyDegree", "value"),
    Input("maxYear", "value"),)
def polynomialRegression(specie, country, source, polyDegree, maxYear):
    maxYear = int(maxYear)

    # Step one: Get FAO data
    countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]

    if specie == None:
        specie = species[0]

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)

    elif country == None:
        fao_data = fao.get_data(countries[0], specie)

    else:
        fao_data = fao.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)

    # Step two: Get woah data
    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        woah_data = woah.get_data(country, specie)

    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census data
    csv_data, csv_index_list, species = API_helpers.helperFunctions.getFormattedCensusData(country, specie)

    # Step 4: Get National data
    nationalData, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie)

    # Build a master dataframe
    master_df = pd.concat([fao_data, woah_data, csv_data.iloc[csv_index_list], nationalData.iloc[nationalData_index_list]])

    # Build the plotly graph
    fig = px.line(master_df,
                x=master_df["year"],
                y=master_df["population"],
                color=master_df["source"],
                markers=True)

    # Build out the polynomial regression lines
    polyDegree = int(polyDegree)
    x = []
    if source != "No Options Available":
        for i in range(1, polyDegree+1):
            #Turn the data into a numpy array
            if source == "FAOSTAT":
                x = fao_data["year"]
                y = fao_data["population"]

            elif source == "WOAH":
                x = woah_data["year"]
                y = woah_data["population"]

            elif source == "UN Census Data":
                x = csv_data.iloc[csv_index_list]["year"]
                y = csv_data.iloc[csv_index_list]["population"]

            else:
                x = nationalData.iloc[nationalData_index_list]["year"]
                y = nationalData.iloc[nationalData_index_list]["population"]

            #Convert to numpy arrays
            x = np.array(x)
            y = np.array(y)

            #Fit the model
            model = PolynomialFeatures(degree=i)
            x_new = model.fit_transform(x.reshape(-1, 1))
            new_model = LinearRegression()
            new_model.fit(x_new, y)

            #Add in any missing years
            for j in range(x[0], x[-1]+1):
                if j not in x:
                    x = np.append(x, j)

            x.sort()

            #Add in the predicted value years
            # x = np.append(x, [j for j in range(x[-1] + 1, maxYear+1)])
            x_new = model.fit_transform(x.reshape(-1, 1))
            ypredict = new_model.predict(x_new)

            fig.add_traces(go.Scatter(x=x, y=ypredict, mode='lines', name='Polynomial Regression Degree ' + str(i)))

            if polyDegree == 3:
                sendPolynomialRegressionOutliersToFile(x, y, ypredict, source, specie, country)

    fig.update_layout(
        title=f"Population of {specie} in {country}",
        xaxis_title="Year",
        yaxis_title="Population",
        legend_title="Sources",
        font= dict(
            size = 18,
            color = "black"
        ),
        plot_bgcolor='white',
        xaxis = dict(
        tickmode='array',
        tickvals = x,
        ticktext = x,
    ),
    )

    fig.update_yaxes(
        type='linear',
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_traces(line=dict(width=5))

    return fig


@app.callback(
    Output("genDataViewerGraph", "figure"),
    Input("species_checklist", "value"),
    Input("country_checklist", "value"))
def update_line_chart(specie, country):
    # Step one: Get FAO data
    countries = ["Greece", "Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]

    if specie == None:
        specie = species[0]

    if country == "USA":
        fao_data = fao.get_data("United%20States%20of%20America", specie)

    elif country == None:
        fao_data = fao.get_data(countries[0], specie)

    else:
        fao_data = fao.get_data(country, specie)

    fao_data = fao.formatFAOData(fao_data)

    # Step two: Get woah data
    if country == "USA":
        woah_data = woah.get_data("United%20States%20of%20America", specie)
    else:
        woah_data = woah.get_data(country, specie)

    woah_data = woah.formatWoahData(woah_data)

    # Step 3: Get Census data
    csv_data, csv_index_list, species = API_helpers.helperFunctions.getFormattedCensusData(country, specie)

    # Step 4: Get National data
    nationalData, nationalData_index_list, species = API_helpers.helperFunctions.getFormattedNationalData(country, specie)

    # Build a master dataframe
    master_df = pd.concat([fao_data, woah_data, csv_data.iloc[csv_index_list], nationalData.iloc[nationalData_index_list]])

    # Build the plotly graph
    fig = px.line(
            master_df,
            x=master_df["year"],
            y=master_df["population"],
            color=master_df["source"],
            markers=True)

    fig.update_yaxes(
        type='linear',
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    fig.update_traces(line=dict(width=5))

    fig.update_layout(
        title=f"Population of {specie} in {country}",
        xaxis_title="Year",
        yaxis_title="Population",
        legend_title="Sources",
        font = dict(
            size=18,
        ),
        plot_bgcolor='white',
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

def returnApp():
    """
    This function is used to create the app and return it to waitress in the docker container
    """
    # If BASE_URL is set, use DispatcherMiddleware to serve the app from that path
    if 'BASE_URL' in os.environ:
        from werkzeug.middleware.dispatcher import DispatcherMiddleware
        app.wsgi_app = DispatcherMiddleware(Flask('dummy_app'), {
            BASE_URL: app.server
        })
        # Add redirect to new path
        @app.wsgi_app.app.route('/')
        def redirect_to_dashboard():
            return redirect(BASE_URL)
        return app.wsgi_app

    # If no BASE_URL is set, just return the app server
    return app.server
