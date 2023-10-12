# Write data to a text file
def writeToTextFile(header, data, filename):
    with open(f"../automatedInconsistencies/{filename}.csv", "w") as file:
        file.write(f"year,{header}\n")

        if type(data) == list:
            for item in data:
                file.write(f"{item}\n")

        elif type(data) == dict:
            for key, value in data.items():
                file.write(f"{key},{value}\n")

        else:
            print("Error: data is not a list or dictionary")


#Convert list of strings to list of floats
def convertStringListToFloatList(list):
    floatList = []
    for item in list:
        floatList.append(float(item))
    return floatList


def sendPolynomialRegressionOutliersToFile(x, y, y_pred, source, specie, country):
    outliers = {}

    y = convertStringListToFloatList(y)
    y_pred = convertStringListToFloatList(y_pred)

    for i in range(len(y)):

        #Distance is a bad variable name, think of the correct term
        distance = y[i] * 0.1
        upperBound = y[i] + distance
        lowerBound = y[i] - distance

        if y_pred[i] > upperBound or y_pred[i] < lowerBound:
            print("y pred = ", y_pred[i])
            outliers[i] = f"{x[i]},{y[i]},{y_pred[i]}"

    #Write outliers to a text file
    header = "data from source,predicted data"
    writeToTextFile(header, outliers, f"{source}_{specie}_{country}_outliers_polynomial_regression")

def upperBound(num):
    return num + (num * 0.1)

def lowerBound(num):
    return num - (num * 0.1)


def calculateFiveYearAvgOutliersInternal(
        fao_percent_change,
        woah_percent_change,
        csv_percent_change,
        national_percent_change,
        yearsArr,
        specie,
        country
    ):
    outliers = {}

    for i in range(1, len(fao_percent_change)):
        if fao_percent_change[i] > upperBound(fao_percent_change[i-1]) or fao_percent_change[i] < lowerBound(fao_percent_change[i-1]):
            outliers[yearsArr[i]] = f"FAOSTAT,{fao_percent_change[i-1]},{fao_percent_change[i]}"

    for i in range(1, len(woah_percent_change)):
        if woah_percent_change[i] > upperBound(woah_percent_change[i-1]) or woah_percent_change[i] < lowerBound(woah_percent_change[i-1]):
            outliers[yearsArr[i]] = f"WOAH,{woah_percent_change[i-1]},{woah_percent_change[i]}"

    for i in range(1, len(csv_percent_change)):
        if csv_percent_change[i] > upperBound(csv_percent_change[i-1]) or csv_percent_change[i] < lowerBound(csv_percent_change[i-1]):
            outliers[yearsArr[i]] = f"Census data,{csv_percent_change[i-1]},{csv_percent_change[i]}"

    for i in range(1, len(national_percent_change)):
        if national_percent_change[i] > upperBound(national_percent_change[i-1]) or national_percent_change[i] < lowerBound(national_percent_change[i-1]):
            outliers[yearsArr[i]] = f"national data,{national_percent_change[i-1]},{national_percent_change[i]}"

    header = "5 year avg,previous 5 year avg"
    writeToTextFile(header, outliers, f"{specie}_{country}_outliers_five_year_avg_INTERNAL")


def calculateFiveYearAvgOutliersExternal(
        fao_percent_change,
        woah_percent_change,
        csv_percent_change,
        national_percent_change,
        yearsArr,
        specie,
        country
    ):
    outliers = []

    for i in range(len(fao_percent_change)):

        #Check fao against all 3
        if fao_percent_change:
            if woah_percent_change and (fao_percent_change[i] > upperBound(woah_percent_change[i]) or fao_percent_change[i] < lowerBound(woah_percent_change[i])):
                outliers.append(f"{yearsArr[i]},FAOSTAT,{fao_percent_change[i]},WOAH,{woah_percent_change[i]}")

            if csv_percent_change and (fao_percent_change[i] > upperBound(csv_percent_change[i]) or fao_percent_change[i] < lowerBound(csv_percent_change[i])):
                outliers.append(f"{yearsArr[i]},FAOSTAT,{fao_percent_change[i]},Census,{csv_percent_change[i]}")

            if national_percent_change and (fao_percent_change[i] > upperBound(national_percent_change[i]) or fao_percent_change[i] < lowerBound(national_percent_change[i])):
                outliers.append(f"{yearsArr[i]},FAOSTAT,{fao_percent_change[i]},National,{national_percent_change[i]}")

        #Check woah against 2
        if woah_percent_change:
            if csv_percent_change and (woah_percent_change[i] > upperBound(csv_percent_change[i]) or woah_percent_change[i] < lowerBound(csv_percent_change[i])):
                outliers.append(f"{yearsArr[i]},WOAH,{woah_percent_change[i]},Census,{csv_percent_change[i]}")

            if national_percent_change and (woah_percent_change[i] > upperBound(national_percent_change[i]) or woah_percent_change[i] < lowerBound(national_percent_change[i])):
                outliers.append(f"{yearsArr[i]},WOAH,{woah_percent_change[i]},National,{national_percent_change[i]}")

        #Check csv against national
        if csv_percent_change and national_percent_change:
            if csv_percent_change[i] > upperBound(national_percent_change[i]) or csv_percent_change[i] < lowerBound(national_percent_change[i]):
                outliers.append(f"{yearsArr[i]},Census,{csv_percent_change[i]},National,{national_percent_change[i]}")

    #Remove instances with
    for i in range(len(outliers) - 1, -1, -1):
        if outliers[i][-1] == "0":
            outliers.pop(i)

    header = "Src,5 year avg,Src,previous 5 year avg"
    writeToTextFile(header, outliers, f"{specie}_{country}_outliers_five_year_avg_EXTERNAL")