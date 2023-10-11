# Write data to a text file
def writeToTextFile(header, data, name):
    with open(f"../automatedInconsistencies/{name}.csv", "w") as file:
        file.write(f"{header}\n")
        for key, value in data.items():
            file.write(f"{key},{value}\n")


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
    header = "year,data from source,predicted data"
    writeToTextFile(header, outliers, f"{source}_{specie}_{country}_outliers_polynomial_regression")