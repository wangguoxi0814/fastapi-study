from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schema.users import UserRequest, UserUpdateRequest
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


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify(password, user.password):
        return None

    return user


# 根据 Token 查询用户：联合查询
async def get_user_by_token(db: AsyncSession, token: str):
    query = (
        select(User)
        .join(UserToken, User.id == UserToken.user_id)
        .where(UserToken.token == token)
        .where(UserToken.expires_at > datetime.now())
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user_info(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    update_ = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(update_)
    if not result.rowcount:
        raise HTTPException(status_code=400, detail="用户不存在,修改个人信息失败！")
    user = await get_user_by_username(db, username)
    return user

# 修改密码: 验证旧密码 → 新密码加密 → 修改密码
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify(old_password, user.password):
        return False

    hashed_new_pwd = security.get_hash(new_password)
    user.password = hashed_new_pwd
    # 更新: 由SQLAlchemy真正接管这个 User 对象，确保可以 commit
    # 不共享Session，或者这个user之前手动commit，对象就会处于游离态，需要add重新添加到Session中
    # 在当前代码架构中，不需要
    # db.add(user)
    print('db.identity_map: ', db.identity_map.keys())
    return True