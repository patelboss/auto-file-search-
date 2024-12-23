from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import logging
from info import *
# Initialize the Motor client and Umongo instance
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance(db)

# Logger setup
LOGGER = logging.getLogger(__name__)

# Define VerifiedUser model
@instance.register
class VerifiedUser(Document):
    user_id = fields.IntField(required=True)  # Store user ID
    verified_at = fields.DateTimeField(required=True)  # Store verification timestamp

    class Meta:
        collection_name = 'verified_users'


# Define Token model
@instance.register
class Token(Document):
    user_id = fields.IntField(required=True)
    token = fields.StrField(required=True)
    is_used = fields.BooleanField(default=False)
    created_at = fields.DateTimeField(default=datetime.utcnow)

    class Meta:
        collection_name = 'tokens'


async def add_verified_user(user_id: int):
    try:
        verification_data = VerifiedUser(
            user_id=user_id,
            verified_at=datetime.utcnow()
        )
        await verification_data.commit()
        LOGGER.info(f'User {user_id} verified and added to the database.')
    except Exception as e:
        LOGGER.error(f'Error while adding verified user: {e}')


async def remove_verified_user(user_id: int):
    try:
        verified_user = await VerifiedUser.find_one({'user_id': user_id})
        if verified_user:
            await verified_user.remove()
            LOGGER.info(f'User {user_id} removed from the verified_users collection.')
    except Exception as e:
        LOGGER.error(f'Error while removing verified user: {e}')


async def is_user_verified(user_id: int):
    try:
        verified_user = await VerifiedUser.find_one({'user_id': user_id})
        if verified_user:
            if verified_user.verified_at + timedelta(seconds=86400) > datetime.utcnow():
                return True
            else:
                await remove_verified_user(user_id)
                return False
        return False
    except Exception as e:
        LOGGER.error(f'Error while checking verification status for user {user_id}: {e}')
        return False


async def save_token(user_id: int, token: str):
    try:
        token_data = Token(
            user_id=user_id,
            token=token,
            is_used=False
        )
        await token_data.commit()
        LOGGER.info(f'Token for user {user_id} saved in the database.')
    except Exception as e:
        LOGGER.error(f'Error while saving token for user {user_id}: {e}')


async def mark_token_as_used(user_id: int, token: str):
    try:
        token_data = await Token.find_one({'user_id': user_id, 'token': token})
        if token_data:
            token_data.is_used = True
            await token_data.commit()
            LOGGER.info(f'Token {token} for user {user_id} marked as used.')
    except Exception as e:
        LOGGER.error(f'Error while marking token as used: {e}')


async def is_token_used(user_id: int, token: str):
    try:
        token_data = await Token.find_one({'user_id': user_id, 'token': token})
        if token_data:
            return token_data.is_used
        return False
    except Exception as e:
        LOGGER.error(f'Error while checking if token {token} is used for user {user_id}: {e}')
        return False
