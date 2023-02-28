# Census Data Quality Research
# Written By Ian McKechnie
# Last Updated: Monday Feb 27, 2023

# Using the interquartile range: We would find the average ROC for the
# growth in animal populations. Then find the interquartile range
# (https://www.scribbr.com/statistics/interquartile-range/) for the data.
# Then add error bars around the data to visualize where approximate outliers are.

import API_helpers.fao as fao
import API_helpers.oie as oie
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import API_helpers.helperFunctions as helperFunctions
import plotly.figure_factory as ff
import numpy as np
import plotly.graph_objects as go


# Step one: Get FAO Data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Cattle"
country = "USA"

if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
else:
    fao_data = fao.get_data(country, specie)

fao_data = fao.formatFAOData(fao_data)

# Step two: Get OIE Data
if country == "USA":
    oie_data = oie.get_data("United%20States%20of%20America", specie)
else:
    oie_data = oie.get_data(country, specie)

oie_data = oie.formatOIEData(oie_data)

# Step 3: Get Census Data
csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie, species)

# Step 4: Get National Data
nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie, species)

# Get the rate of change of each point in each data set and put it into arrays
fao_roc = helperFunctions.getROC(fao_data, "population")
oie_roc = helperFunctions.getROC(oie_data, "population")
csv_roc = helperFunctions.getROC(csv_data, "population")
national_roc = helperFunctions.getROC(nationalData, "population")

# print("oie", oie_roc.tail())
# print("csv", csv_roc)
# print("natonal", national_roc.tail())

# Get the year range from the user
startYear = 1960
endYear = 2019

while True:
    startYear = input("What is your start year? ").strip()
    if startYear.isdigit():
        startYear = int(startYear)
        break
    else:
        print("Please enter a valid year")

while True:
    endYear = input("What is your end year? ").strip()
    if endYear.isdigit():
        endYear = int(endYear)
        break
    else:
        print("Please enter a valid year")

#Get the IQR for FAO
fao_data = fao_roc.values.tolist()
fao_dict = {}

for elem in fao_data:
    fao_dict[int(elem[0])] = elem[1]

fao_iqr_list = []
for i in range(startYear, endYear):
    #Add all the years that exist in the range
    try:
        fao_iqr_list.append(fao_dict[i])
    except:
        continue

firstHalf = fao_iqr_list[:len(fao_iqr_list)//2]
secondHalf = fao_iqr_list[len(fao_iqr_list)//2:]

firstQuartile = firstHalf[:len(firstHalf)//2]
secondQuartile = firstHalf[len(firstHalf)//2:]
thirdQuartile = secondHalf[:len(secondHalf)//2]
fourthQuartile = secondHalf[len(secondHalf)//2:]

if firstQuartile == [] or thirdQuartile == []:
    fao_iqr = None
else:
    fao_q1 = np.median(firstQuartile)
    fao_q3 = np.median(thirdQuartile)
    fao_iqr = fao_q3 - fao_q1

print("FAO IQR", fao_iqr)

#Get the IQR for OIE
oie_data = oie_roc.values.tolist()
oie_dict = {}

for elem in oie_data:
    oie_dict[int(elem[0])] = elem[1]

oie_iqr_list = []
for i in range(startYear, endYear):
    #Add all the years that exist in the range
    try:
        oie_iqr_list.append(oie_dict[i])
    except:
        continue

firstHalf = oie_iqr_list[:len(oie_iqr_list)//2]
secondHalf = oie_iqr_list[len(oie_iqr_list)//2:]

firstQuartile = firstHalf[:len(firstHalf)//2]
secondQuartile = firstHalf[len(firstHalf)//2:]
thirdQuartile = secondHalf[:len(secondHalf)//2]
fourthQuartile = secondHalf[len(secondHalf)//2:]

if firstQuartile == [] or thirdQuartile == []:
    oie_iqr = None
else:
    oie_q1 = np.median(firstQuartile)
    oie_q3 = np.median(thirdQuartile)
    oie_iqr = oie_q3 - oie_q1

print("OIE IQR", oie_iqr)

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

firstHalf = csv_iqr_list[:len(csv_iqr_list)//2]
secondHalf = csv_iqr_list[len(csv_iqr_list)//2:]

firstQuartile = firstHalf[:len(firstHalf)//2]
secondQuartile = firstHalf[len(firstHalf)//2:]
thirdQuartile = secondHalf[:len(secondHalf)//2]
fourthQuartile = secondHalf[len(secondHalf)//2:]

if firstQuartile == [] or thirdQuartile == []:
    csv_iqr = None
else:
    csv_q1 = np.median(firstQuartile)
    csv_q3 = np.median(thirdQuartile)
    csv_iqr = csv_q3 - csv_q1

print("csv_iq r", csv_iqr)


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

firstHalf = national_iqr_list[:len(national_iqr_list)//2]
secondHalf = national_iqr_list[len(national_iqr_list)//2:]

firstQuartile = firstHalf[:len(firstHalf)//2]
secondQuartile = firstHalf[len(firstHalf)//2:]
thirdQuartile = secondHalf[:len(secondHalf)//2]
fourthQuartile = secondHalf[len(secondHalf)//2:]

if firstQuartile == [] or thirdQuartile == []:
    national_iqr = None
else:
    national_q1 = np.median(firstQuartile)
    national_q3 = np.median(thirdQuartile)
    national_iqr = national_q3 - national_q1

print("national_iqr ", national_iqr)