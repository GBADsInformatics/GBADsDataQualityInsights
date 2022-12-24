# Census Data Qaulity Research
# Written By Ian McKechnie
# Last Updated: Tuesday Dec 20, 2022
import API_helpers.fao as fao


countries = ["Ethiopia", "Canada", "USA", "Ireland", "India", "Brazil", "Botswana", "Egypt", "South Africa", "Idndonisia", "China", "Australia", "New Zealand", "Japan", "Mexico", "Argentina", "Chile"]
species = ["Cattle","Sheep","Goats","Pigs","Chickens"]

country = countries[0]
specie = species[0]

# Step one: Get FAO data
ans = fao.get_fao_data(country, specie)

# Step two: Get OIE data


# Step 3: Get Census data

# Step 4: Get National data