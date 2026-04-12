import pandas as pd

def preprocess_data(path):

    data = pd.read_csv(path)

    # Remove ID column
    data = data.drop("transaction_id", axis=1)

    # Convert merchant_category → numbers
    data = pd.get_dummies(data, columns=["merchant_category"])

    return data
