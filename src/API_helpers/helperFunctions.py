import pandas as pd

#Gets the rate of change (averaged across the time frame) for a given dataframe
#Params
#df: The dataframe to get the rate of change for
#field: The field or column name to get the rate of change for
#Returns: A dataframe with the rate of change for each year, where rateOfChange is a float (%%.%%%%%%%%...)
def getROC(df, field):
    roc = pd.DataFrame(columns=['year', "rateOfChange"])

    for i in range(len(df) - 1):
        a = int(df.iloc[i+1][field])
        b = int(df.iloc[i][field])
        a_year = int(df.iloc[i+1]['year'])
        b_year = int(df.iloc[i]['year'])
        rate = ((a-b)/a * 100) / (b_year - a_year)
        data = [df.iloc[i]['year'], rate]
        row = pd.DataFrame([data], columns=['year', "rateOfChange"])
        roc = pd.concat([roc, row], axis=0)

    return roc

# Gets the growth rate for a given dataframe
# Parmas
# df: The dataframe to get the growth rate for
# field: The field or column name to get the growth rate for
# Returns: A dataframe with the growth rate for each year, where growthRate is a float (%%.%%%%%%%%...)
def growthRate(df, field, specie):
    growthRates = pd.DataFrame(columns=['year', "growthRate"])

    if len(df.columns) == 0:
        return growthRates

    df = df[df['species'] == specie]

    for i in range(len(df) - 1):

        rate = ((int(df.iloc[i+1][field]) - int(df.iloc[i][field]))/ int(df.iloc[i][field])) * 100
        data = [df.iloc[i]['year'], rate]
        row = pd.DataFrame([data], columns=['year', "growthRate"])
        growthRates = pd.concat([growthRates, row], axis=0)

    return growthRates


def str2frame(estr, source, sep = ',', lineterm = '\n'):
    source = source.upper()
    dat = [x.split(sep) for x in estr.split(lineterm)][1:-1]
    if source == "FAOSTAT":
        df = pd.DataFrame(dat, columns=['iso3', "country", 'year', 'species', 'population'] )
    else:
        df = pd.DataFrame(dat, columns=["country", 'year', 'species', 'population', "source"] )
    return df


def getFormattedCensusData(country, specie, species = []):

    try:
        csv_data = pd.read_csv(f"censusData/{country}.csv")
        species = species + csv_data["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species
        csv_index_list = csv_data[(csv_data['species'] == specie)].index.tolist()

    except Exception as e:
        print("Error, count not find the correct csv file for the census data")
        csv_data = pd.DataFrame()
        csv_index_list = []

    return csv_data, csv_index_list, species


def getFormattedNationalData(country, specie, species = []):

    print("species before national data: ", species)

    try:
        nationalData = pd.read_csv(f"nationalData/{country}.csv")
        species = species + nationalData["species"].tolist() # Add the species from the csv file to the list of species
        species = list(dict.fromkeys(species))  # Remove duplicates from the list of species
        nationalData_index_list = nationalData[(nationalData['species'] == specie)].index.tolist()
        print(f"Success finding national data for {country}")

    except:
        print(f"Error, count not find the correct csv file for the national data for {country}")
        nationalData = pd.DataFrame()
        nationalData_index_list = []

    print("species after national data: ", species)
    return nationalData, nationalData_index_list, species