from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import users

from schema.users import UserRequest

router = APIRouter(prefix="/api/user", tags=['users'])

@router.post('/register')
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 查询用户是否存在
    exist_user = await users.get_user_by_username(db, user_data.username)
    if exist_user:
        raise HTTPException(status_code=400, detail="用户已存在")
    # 创建用户
    user = await users.create_user(db, user_data)
    # 创建Token
    token = await users.create_token(db, user)
    return {
      "code": 200,
      "message": "注册成功",
      "data": {
        "token": token,
        "userInfo": {
          "id": user.id,
          "username": user.username,
          "bio": user.bio,
          "avatar": user.avatar
        }
      }
    }