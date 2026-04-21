import pickle

with open("model/xgb_model.pkl", "rb") as f:
    model = pickle.load(f)

print("Model expects features:", model.n_features_in_)