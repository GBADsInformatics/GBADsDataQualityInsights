import pandas as pd

def getGrowthRate(fao_data):
    growthRates = pd.DataFrame(columns=['year', 'growthRate'])

    for i in range(len(fao_data) - 1):
        print(fao_data.iloc[i+1]['population'])
        rate = ((int(fao_data.iloc[i+1]['population']) - int(fao_data.iloc[i]['population']))/ int(fao_data.iloc[i]['population'])) * 100
        growthRates = growthRates.append({'year': fao_data.iloc[i]['year'], 'growthRate': rate}, ignore_index=True)


    return growthRates