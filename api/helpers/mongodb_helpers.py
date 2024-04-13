import datetime
import os

from bson import ObjectId
from pymongo import MongoClient

# Get MongoDB connection details from environment variables
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("MONGO_DB")
MONGO_COLLECTION = os.environ.get("MONGO_DB_COLLECTION")

# Function to save metadata about the user in MongoDB
def save_user_metadata(fullname, email, voice_file_id):
    # Generate a timestamp for the video upload
    timestamp = datetime.utcnow()
    # Create metadata to be stored in MongoDB
    metadata = {
        "fullname": fullname,
        "email": email,
        "voice_file_id": voice_file_id,
        "timestamp": timestamp,
        "planned": False  # Initial status, not yet planned
    }
    db_collection = _connect_to_mongo()
    # Insert the metadata into the MongoDB collection and retrieve the user ID
    user_id = db_collection.insert_one(metadata).inserted_id
    return user_id

def update_user_register_planned_date(user_id, logical_date):
    db_collection = _connect_to_mongo()
    # Update the MongoDB document with "planned" flag and date
    db_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"planned": True, "planned_date": logical_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}}
    )

def find_user_details(user_id):
    """
    Find user details by user ID.

    Parameters:
    - user_id (str): The ID of the user to search for.

    Returns:
    - dict or None: A dictionary containing the user details if found, or None if not found.
    """
    db_collection = _connect_to_mongo()  # Establish connection to MongoDB
    user_info = db_collection.find_one({"_id": ObjectId(user_id)})  # Find user details by ID
    return user_info

def delete_user_details(user_id):
    """
    Delete user details by user ID.

    Parameters:
    - user_id (str): The ID of the user to delete.

    Returns:
    - None
    """
    db_collection = _connect_to_mongo()  # Establish connection to MongoDB
    db_collection.delete_one({"_id": ObjectId(user_id)})  # Delete user details by ID

# Connect to MongoDB using the provided URI
def _connect_to_mongo():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    db_collection = db[MONGO_COLLECTION]
    return db_collection