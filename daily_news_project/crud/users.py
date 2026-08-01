from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schema.users import UserRequest
from utils import security


async def get_user_by_username(db: AsyncSession, username: str):
    stmt = await db.execute(select(User).where(User.username == username))
    return stmt.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserRequest):
    user = User(**user_data.__dict__)
    crypt_pwd = security.get_hash(user.password)
    user.password = crypt_pwd
    db.add(user)
    return user


async def create_token(db: AsyncSession, user: User):
    expired_time = datetime.now() + timedelta(days=7)
    token = security.get_token_str()
    stmt = await db.execute(
        select(UserToken)
        .where(
            UserToken.user_id == user.id
        )
    )
    exist_token = stmt.scalar_one_or_none()
    if exist_token:
        exist_token.token = token
        exist_token.expires_at = expired_time
    else:
        user_token = UserToken(user_id=user.id, token=security.get_token_str(), expires_at=expired_time)
        db.add(user_token)
    return token

