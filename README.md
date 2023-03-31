# Census Data Quality Research
By Ian McKechnie

For the Global Burden of Animal Diseases

Check us out! https://gbads-oie.com

## Description of this Project
As the saying goes, "Garbage in, Garbage out". This project is to evaluate the quality of data from the FAOSTAT, WOAH, UN Census, and individual country data for future modelers to understand the quality of the data before they use it in their models. You can read the report on the findings from using the tools in this repo. The report can be found here: https://docs.google.com/document/d/1gRUBvgBTjukJKQZnqwlkcEbSRYD6RK6S3SDPTf2eX94/edit?usp=sharing

#### In this repo there is one program to view the data, three to analyze data quality, and one to predict future data.

To view the data you will need to run the `generalDataViewer.py` dashboard located in the analysisTools folder.

The 3 analysis dashboards are also located in the analysisTools folder. They are as follows

1. `5yearPopulationAvg.py`

This program takes the average rate of change for the increase in a species population for each year for a given country for each data source. This is used to compare the rate of change between each data source and if one is substantially bigger than the other two it could be concluded that there is a higher chance that it is wrong.

![Alt text](lib/5yearAvgExample.png?raw=true "Example")

2. `growthRates.py`

If you take all the growth rates for a population of animals in a country every year, and you plot every yearly growth rate, it will produce a normal curve. From there we can spot outliers by defining a cut off of 3 standard deviations. Past this point we can label those points as outliers and conclude that there is a high chance that they are inaccuracies.

![Alt text](lib/growthRatesExample.png?raw=true "Example")

3. `IQR.py`

This program takes the interquartile range of the data and compares it to the average rate of change. If the average rate of change is greater than the interquartile range, then it is likely that the data is inaccurate.

![Alt text](lib/iqrExample.png?raw=true "Example")

The program for viewing data

1. `generalDataViewer.py`

This program is a dashboard that allows you to view the data from the FAOSTAT, WOAH, UN Census, and individual country data for a given country and species.

![Alt text](lib/generalDataViewExample.png?raw=true "Example")

The program for predicting future data

1. `polyRegression.py`

This Dashboard shows the user the graph from `generalDataViewer.py` but allows you to configure a polynomial regression model to predict future data. The user can also configure the degree of the polynomial regression model. The user can also configure the number of years to predict into the future.

![Alt text](lib/polyRegressionLineExample.png?raw=true "Example")

## To Run The DashBoard
Make sure you have pip/pip3 installed

Navigate to into the directory, then run

`cd src`

Then run

`pip3 (or pip) install -r requirements.txt`


Finally run

`python3 (or python) generalDatViewer.py`

or
`python3 (or python) growthRates.py`

or
`python3 (or python) IQR.py`

## To Run the Prediciton Model
Make sure you have pip/pip3 installed

Navigate to into the directory, then run

`cd src`

Then run

`pip3 (or pip) install -r requirements.txt`


Finally run

`python3 (or python) polyRegression.py`

## Data sources
- FAO and WOAH/OIE come from the API
- Census data from countries is in the S3 bucket (on AWS)
- National data needs to be harvested from Stats agencies of countries

## Counties
- Ethiopia
- Canada
- USA
- Ireland
- India
- Brazil
- Botswana
- Egypt
- South Africa
- Indonesia
- China
- Australia
- New Zealand
- Japan
- Mexico
- Argentina
- Chile

## Possible species that can be viewed (depends on country)
Cattle,
Beef Cattle,
Dairy Cows,
Sheep,
Goats,
Pigs,
Chickens,
Horses,
Buffaloes,
Ducks,
Turkeys,
Ostrichs,
Asses and Mules,
Mules,
Asses,
Wild Boars,
Boar,
Bison,
Elks,
Llamas/Alpacas,
Alpacas and Llamas,
Ostriches and Emus,
Alpacas,
Llamas,
Deer,
Minks,
Foxes,
Rabbits,
Other Fowls,
Geese,
Guinea Pigs,
Poultry,
Camels,
Pigeons,
Geese and Ducks,
Bees,
Beehives,
Mithuns (Bovine),
Equines,
Broilers,
Laying hens,
Hen,
“Mules, Asses”,