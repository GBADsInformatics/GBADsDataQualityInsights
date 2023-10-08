# Census Data Quality Research
By Ian McKechnie

For the Global Burden of Animal Diseases

Check us out! [GBADsKE](https://www.gbadske.org)

## Description of this roject
As the saying goes, "Garbage in, Garbage out". This project is to evaluate the quality of data from the FAOSTAT, WOAH, UN Census, and individual country data for future modelers to understand the quality of the data before they use it in their models. You can read the report on the findings from using the tools in this repo.


Findings from this tool are currently pending review before being published. Stay tunned on the GBADsKE website for more information.

## To use this project
Run these commands in the project folder

```cd src```

```pip3 install -r requirements.txt```

```python3 app.py```

## Data sources
- FAOSTAT and WOAH/OIE come from the API
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
