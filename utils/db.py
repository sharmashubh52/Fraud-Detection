#from pymongo import MongoClient

# Connect to MongoDB
#client = MongoClient("mongodb://localhost:27017/")

# Create database
#db = client["fraud_detection_db"]

# Create collection
#transactions_collection = db["transactions"]

from pymongo import MongoClient
import os

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://labhvaidh_db_user:rxbh2xoA0E8V5NJd@cluster0.cawva5c.mongodb.net/?appName=Cluster0"
)

client = MongoClient(MONGO_URI)
db = client["fraud_detection_db"]
transactions_collection = db["transactions"]
