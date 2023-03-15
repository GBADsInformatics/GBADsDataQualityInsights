# Census Data Quality Research
# Written By Ian McKechnie
# Last Updated: Monday Feb 27, 2023

# Using the interquartile range: We would find the average ROC for the
# growth in animal populations. Then find the interquartile range
# (https://www.scribbr.com/statistics/interquartile-range/) for the data.
# Then add error bars around the data to visualize where approximate outliers are.

import API_helpers.fao as fao
import API_helpers.woah as woah
import pandas as pd
import plotly.express as px
import API_helpers.helperFunctions as helperFunctions
import numpy as np

# Step one: Get FAO Data
countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Indonesia", "China", "Australia", "NewZealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]
specie = "Goats"
country = "South Africa"

# Step one: Get FAO Data and woah Data
if country == "USA":
    fao_data = fao.get_data("United%20States%20of%20America", specie)
    woah_data = woah.get_data("United%20States%20of%20America", specie)
else:
    fao_data = fao.get_data(country, specie)
    woah_data = woah.get_data(country, specie)

fao_data = fao.formatFAOData(fao_data)
woah_data = woah.formatWoahhData(woah_data)

# Step 3: Get Census Data
csv_data, csv_index_list, species = helperFunctions.getFormattedCensusData(country, specie, species)

#Only get the rows that have the correct specie
new_csv_data = []
for index, row in csv_data.iterrows():
    if row['species'] == specie:
        new_csv_data.append( [row['year'], row['population']] )

csv_data = pd.DataFrame(new_csv_data, columns = ["year", "population"])

# Step 4: Get National Data
nationalData, nationalData_index_list, species = helperFunctions.getFormattedNationalData(country, specie, species)

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
national_roc = helperFunctions.getROC(nationalData, "population")

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

#Get the IQR for woah
woah_data = woah_roc.values.tolist()
woah_dict = {}

for elem in woah_data:
    woah_dict[int(elem[0])] = elem[1]

woah_iqr_list = []
for i in range(startYear, endYear):
    #Add all the years that exist in the range
    try:
        woah_iqr_list.append(woah_dict[i])
    except:
        continue

firstHalf = woah_iqr_list[:len(woah_iqr_list)//2]
secondHalf = woah_iqr_list[len(woah_iqr_list)//2:]

firstQuartile = firstHalf[:len(firstHalf)//2]
secondQuartile = firstHalf[len(firstHalf)//2:]
thirdQuartile = secondHalf[:len(secondHalf)//2]
fourthQuartile = secondHalf[len(secondHalf)//2:]

if firstQuartile == [] or thirdQuartile == []:
    woah_iqr = None
else:
    woah_q1 = np.median(firstQuartile)
    woah_q3 = np.median(thirdQuartile)
    woah_iqr = woah_q3 - woah_q1

print("WOAH IQR", woah_iqr)

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

csv_iqr = None
sv_q1 = None
csv_q3 = None
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


#Get the upper and lower fence
fao_upperFence = fao_q3 + (1.5 * fao_iqr)
fao_lowerFence = fao_q1 - (1.5 * fao_iqr)

woah_upperFence = woah_q3 + (1.5 * woah_iqr)
woah_lowerFence = woah_q1 - (1.5 * woah_iqr)

if csv_iqr:
    csv_upperFence = csv_q3 + (1.5 * csv_iqr)
    csv_lowerFence = csv_q1 - (1.5 * csv_iqr)

if national_iqr:
    national_upperFence = national_q3 + (1.5 * national_iqr)
    national_lowerFence = national_q1 - (1.5 * national_iqr)


# This next section is for the boxplots, you don't need the above data for this

#Fao
faoCopy = fao_roc['rateOfChange'].copy().to_frame()
faoNewCol = ['FAO' for i in range(len(faoCopy))]
faoCopy['Source'] = faoNewCol

masterDf = faoCopy.copy()

#woah
woahCopy = woah_roc['rateOfChange'].copy().to_frame()
woahNewCol = ['WOAH' for i in range(len(woahCopy))]
woahCopy['Source'] = woahNewCol

masterDf = pd.concat([masterDf, woahCopy])

#csv
csvCopy = csv_roc['rateOfChange'].copy().to_frame()
csvNewCol = ['UN Census Data' for i in range(len(csvCopy))]
csvCopy['Source'] = csvNewCol

masterDf = pd.concat([masterDf, csvCopy])

#National
nationalCopy = national_roc['rateOfChange'].copy().to_frame()
nationalNewCol = ['National Census Bureau' for i in range(len(nationalCopy))]
nationalCopy['Source'] = nationalNewCol

masterDf = pd.concat([masterDf, nationalCopy])

fig = px.box( masterDf, y="rateOfChange", x="Source", points="all")
fig.show()
