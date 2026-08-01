import uuid

from passlib.context import CryptContext

# 创建密码加密上下⽂
crypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_hash(content: str):
    return crypt_context.hash(content)

def get_token_str():
    return str(uuid.uuid4())