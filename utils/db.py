from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create database
db = client["fraud_detection_db"]

# Create collection
transactions_collection = db["transactions"]

