from pymongo import MongoClient
from datetime import datetime, date
import pytz
import asyncio
import logging
from info import DATABASE_URI

# Initialize MongoDB client and database
client = MongoClient(DATABASE_URI)
db = client['verify']  # Replace with your actual database name
verified_collection = db['verified_users']

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def check_verificationdb(userid):
    """
    Check if the user is verified for today's date.
    Returns True if verified for today, else False.
    """
    logger.info(f"Checking verification status for user_id: {userid}")
    verified_user = verified_collection.find_one({'user_id': userid})

    if verified_user:
        # Check if the verification date matches today's date
        verification_date = verified_user['verified_at']  # Stored as a string in 'YYYY-MM-DD' format
        today = date.today().strftime('%Y-%m-%d')
        logger.info(f"Verification date for user_id {userid}: {verification_date}")

        if verification_date == today:
            logger.info(f"User_id {userid} is verified for today.")
            return True  # Verified for today's date
        else:
            # Remove expired verification
            logger.warning(f"Verification expired for user_id {userid}. Removing record.")
            remove_expired_verification(userid)  # Call the cleanup function
            return False  # Expired verification
    else:
        logger.info(f"User_id {userid} is not verified.")
        return False  # User not verified

async def verify_userdb(userid):
    """
    Save the user's verification status with today's date.
    """
    today = date.today().strftime('%Y-%m-%d')  # Store as 'YYYY-MM-DD'
    verified_data = {
        'user_id': userid,
        'verified_at': today  # Store today's date as a string
    }

    logger.info(f"Saving verification status for user_id {userid} with data: {verified_data}")

    # Insert or update the user's verification status in MongoDB
    result = verified_collection.update_one(
        {'user_id': userid},
        {'$set': verified_data},
        upsert=True  # Create the document if it doesn't exist
    )
    if result.upserted_id or result.modified_count > 0:
        logger.info(f"Verification status successfully saved for user_id {userid}.")
    else:
        logger.warning(f"No changes made for user_id {userid}. Already up-to-date.")

def remove_expired_verification(userid):
    """
    Remove expired verification from the database.
    """
    logger.info(f"Removing expired verification for user_id {userid}.")
    result = verified_collection.delete_one({'user_id': userid})
    if result.deleted_count > 0:
        logger.info(f"Expired verification successfully removed for user_id {userid}.")
    else:
        logger.warning(f"No expired verification found for user_id {userid}.")
