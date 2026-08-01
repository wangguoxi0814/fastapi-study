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

def verify(content: str, hash_str: str):
    """
    比对明文内容加密后和已有加密内容是否一致

    :param content:  明文内容
    :param hash_str: 密文内容
    :return: bool
    """
    return crypt_context.verify(content, hash_str)
