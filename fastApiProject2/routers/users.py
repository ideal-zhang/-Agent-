from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from config.db_config import get_db
from crud import users
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix = "/api/user", tags=["users"])

@router.post('/register')
async def register(user_data: UserRequest ,db: AsyncSession = Depends(get_db)):
    existing_user = await users.get_users(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info = UserInfoResponse.model_validate(user))
    return success_response(message = "注册成功", data = response_data)

@router.post('/login')
async def login(user_data: UserRequest ,db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info = UserInfoResponse.model_validate(user))
    return success_response(message="登陆成功", data = response_data)

@router.get('/info')
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取成功", data=UserInfoResponse.model_validate(user))

@router.put('/update')
async def update_user_info  (user_data: UserUpdateRequest ,
                 user: User = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="更新信息成功", data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def change_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.change_psw(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请重试")
    return success_response(message="修改密码成功")