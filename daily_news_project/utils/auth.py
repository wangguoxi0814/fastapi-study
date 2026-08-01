import token

from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users

# 定义 OAuth2 安全方案，Swagger 会显示 Authorize 按钮
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


# 整合 根据 Token 查询用户，返回用户
async def get_current_user(
        authorization: str = Header(..., alias='Authorization', description="Bearer {token}"),
        db: AsyncSession = Depends(get_db)
):
    # token = authorization.replace("Bearer ", "")
    token = authorization
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌或已经过期的令牌")

    return user


# OAuth 2方法，可以在docs中使用Token
async def get_oauth2_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌或已经过期的令牌")

    return user
