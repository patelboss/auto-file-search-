from pymongo import MongoClient
from datetime import datetime, date
import pytz
import asyncio
import logging
from info import DATABASE_URI

# Initialize MongoDB client and database (replace with your connection details)
client = MongoClient(DATABASE_URI)
db = client['verify']  # replace 'your_database' with your actual database name
verified_collection = db['verified_users']

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def check_verificationdb(userid):
    """
    Check if the user is verified within the last 24 hours.
    Returns True if verified, else False.
    """
    logger.info(f"Checking verification status for user_id: {userid}")
    verified_user = verified_collection.find_one({'user_id': userid})

    if verified_user:
        # Check if the verification is within the last 24 hours
        verification_time = verified_user['verified_at']
        tz = pytz.timezone('Asia/Kolkata')
        logger.info(f"Verification time for user_id {userid}: {verification_time}")

        if verification_time > datetime.today():
            logger.info(f"User_id {userid} is verified within the last 24 hours.")
            return True  # Verified within the last 24 hours
        else:
            # Remove expired verification
            logger.warning(f"Verification expired for user_id {userid}. Removing record.")
            await verified_collection.delete_one({'user_id': userid})
            return False  # Expired verification
    else:
        logger.info(f"User_id {userid} is not verified.")
        return False  # User not verified

async def verify_userdb(userid):
    """
    Save the user's verification status with the current timestamp.
    """
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    verified_data = {
        'user_id': userid,
        'verified_at': today  # Store the current UTC time for verification
    }

    logger.info(f"Saving verification status for user_id {userid} with data: {verified_data}")

    # Insert or update the user's verification status in MongoDB
    result = await verified_collection.update_one(
        {'user_id': userid},
        {'$set': verified_data},
        upsert=True  # Create the document if it doesn't exist
    )
    if result.upserted_id or result.modified_count > 0:
        logger.info(f"Verification status successfully saved for user_id {userid}.")
    else:
        logger.warning(f"No changes made for user_id {userid}. Already up-to-date.")

async def remove_expired_verification(userid):
    """
    Remove expired verification (older than 24 hours) from the database.
    """
    logger.info(f"Removing expired verification for user_id {userid}.")
    result = await verified_collection.delete_one({'user_id': userid})
    if result.deleted_count > 0:
        logger.info(f"Expired verification successfully removed for user_id {userid}.")
    else:
        logger.warning(f"No expired verification found for user_id {userid}.")
