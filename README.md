# census_data_quality_research
## Goal of this project
Establish data quality evaluation from diverse data sources. This can be done by comparing:
- Census year data
- National data
- FAOSTAT data
- WOAH/OIE data

The goal is to present this data in plots and tables with points, lines, and error bars to visualize the difference between the data sources. Should look like this image

![Alt text](lib/graphExample.png?raw=true "Example")

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
- Idndonisia
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