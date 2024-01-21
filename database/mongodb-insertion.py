import pandas as pd
from pymongo import MongoClient

# Read CSV file into a pandas DataFrame
csv_file_path = r'C:\Users\hadde\Downloads\cars.csv'  # Replace with the actual path to your CSV file
df = pd.read_csv(csv_file_path)

# MongoDB connection settings
mongo_uri = 'mongodb://localhost:27017/'  # Replace with your MongoDB connection URI
database_name = 'cars'            # Replace with your MongoDB database name
collection_name = 'carsales'        # Replace with your MongoDB collection name

# Connect to MongoDB
client = MongoClient(mongo_uri)
database = client[database_name]
collection = database[collection_name]

# Convert DataFrame to dictionary records and insert into MongoDB
records = df.to_dict(orient='records')
collection.insert_many(records)

# Close MongoDB connection
client.close()

print(f'Data from CSV file inserted into MongoDB collection: {collection_name}')
