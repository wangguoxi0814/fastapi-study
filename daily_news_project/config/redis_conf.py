import json
from functools import wraps
from typing import Any, Callable, Union

import redis.asyncio as aredis
from fastapi.encoders import jsonable_encoder

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
PASSWORD = ''  # 暂未设置密码
REDIS_DB = 0

# 创建 Redis 的连接对象
aredis_client = aredis.Redis(
    host=REDIS_HOST,  # Redis 服务器的主机地址
    port=REDIS_PORT,  # Redis 端口号
    db=REDIS_DB,  # Redis 数据库编号，0~15
    decode_responses=True  # 是否将字节数据解码为字符串
)


async def get_cache(key):
    """
    获取缓存
    :param key:
    :return:
    """
    try:
        data = await aredis_client.get(key)
        if data:
            # List\Dict复杂对象存入会转为JSON字符串，这里转回List\Dict复杂对象
            # 如果本身就是str简单数据类型，也不会受影响
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None


async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        # 任何数据都转为JSON.ensure_ascii=False中文正常保存
        data = json.dumps(value, ensure_ascii=False)
        await aredis_client.setex(key, expire, data)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False


def serialize(obj):
    """将 ORM 对象或对象列表转为可序列化的 dict/list"""
    return jsonable_encoder(obj)


# 旁路缓存装饰器
class CacheAside:
    """
    旁路缓存装饰器（Cache-Aside Pattern）

    :param key: 缓存 key，支持三种方式：
        - 字符串: "news:categories"
        - 字符串模板: "news:categories:{offset}:{limit}"（自动填充 kwargs）
        - 函数: lambda offset, limit: f"news:categories:{offset}:{limit}"
    :param expire: 过期时间（秒）
    """

    def __init__(self, key: str | Callable[..., str], expire: int = 3600):
        self.key = key
        self.expire = expire

    def _resolve_key(self, *args, **kwargs) -> str:
        """根据参数生成缓存 key"""
        if callable(self.key):
            # key 是函数，调用它生成 key
            return self.key(*args, **kwargs)
        elif isinstance(self.key, str) and "{" in self.key:
            # key 是字符串模板，用 kwargs 填充
            return self.key.format(**kwargs)
        else:
            # key 是普通字符串
            return self.key

    def __call__(self, func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            cache_key = self._resolve_key(*args, **kwargs)
            data = await get_cache(key=cache_key)
            print(f'cache decorator: {cache_key} -> {data}')
            if not data:  # 缓存未命中
                data = await func(*args, **kwargs)
                val = serialize(data)
                set_result = await set_cache(key=cache_key, value=val, expire=self.expire)
                print(f'cache decorator set: {cache_key} -> {set_result}')
            return data
        return decorator