import pandas as pd

#Gets the rate of change for a given dataframe
#Params
#df: The dataframe to get the rate of change for
#field: The field or column name to get the rate of change for
#Returns: A dataframe with the rate of change for each year, where rateOfChange is a float (%%.%%%%%%%%...)
def getROC(df, field):
    roc = pd.DataFrame(columns=['year', "rateOfChange"])

    # print(df)
    # print("Type of df: ", type(df))

    for i in range(len(df) - 1):
        a = int(df.iloc[i+1][field])
        b = int(df.iloc[i][field])
        rate = (a-b)/a * 100
        data = [df.iloc[i]['year'], rate]
        row = pd.DataFrame([data], columns=['year', "rateOfChange"])
        roc = pd.concat([roc, row], axis=0)

    return roc

# Gets the growth rate for a given dataframe
# Parmas
# df: The dataframe to get the growth rate for
# field: The field or column name to get the growth rate for
# Returns: A dataframe with the growth rate for each year, where growthRate is a float (%%.%%%%%%%%...)
def growthRate(df, field):
    growthRates = pd.DataFrame(columns=['year', "growthRate"])

    for i in range(len(df) - 1):
        rate = ((int(df.iloc[i+1][field]) - int(df.iloc[i][field]))/ int(df.iloc[i][field])) * 100
        data = [df.iloc[i]['year'], rate]
        row = pd.DataFrame([data], columns=['year', "growthRate"])
        growthRates = pd.concat([growthRates, row], axis=0)

    return growthRates


def str2frame(estr, source, sep = ',', lineterm = '\n'):
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    if source == "fao":
        df = pd.DataFrame(dat, columns=['iso3', "country", 'year', 'species', 'population'] )
    elif source == "oie":
        df = pd.DataFrame(dat, columns=["country", 'year', 'species', 'population', "source"] )
    return df


def getFormattedCensusData(country, specie, species):
    print("Country: ", country)
    print("Specie: ", specie)
    print("Species: ", species)

    try:
        csv_data = pd.read_csv(f"censusData/{country}.csv")
        species = species + csv_data["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species
        csv_index_list = csv_data[(csv_data['species'] == specie)].index.tolist()

    except:
        print("Error, count not find the correct csv file")
        csv_data = pd.DataFrame()
        csv_index_list = []

    return csv_data, csv_index_list, species

def getFormattedNationalData(country, specie, species):

    try:
        nationalData = pd.read_csv(f"nationalData/{country}.csv")
        #Add the species from the national data
        species = species + nationalData["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species
        nationalData_index_list = nationalData[(nationalData['species'] == specie)].index.tolist()

    except:
        print("Error, count not find the correct csv file")
        nationalData = pd.DataFrame()
        nationalData_index_list = []

    return nationalData, nationalData_index_list, species