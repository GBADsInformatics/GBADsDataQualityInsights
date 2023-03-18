# census_data_quality_research
## Goal of this project
Establish data quality evaluation from diverse data sources. This can be done by comparing:
- Census year data
- National data
- FAOSTAT data
- WOAH/OIE data

The goal is to present this data in plots and tables with points, lines, and error bars to visualize the difference between the data sources. Should look like this image

![Alt text](lib/graphExample.png?raw=true "Example")

## To Run The DashBoard
Make sure you have pip/pip3 installed

Run

`pip3 (or pip) install -r requirements.txt`

Then run

`cd src`

Finally run
`python3 (or python) generalDatViewer.py`

or
`python3 (or python) growthRates.py`

or
`python3 (or python) IQR.py`

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

## Species being checked against
- Cattle
- Sheep
- Goats
- Pigs
- Chickens