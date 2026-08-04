import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from utils import response


class LogMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        print('log middleware begin')
        is_auth = True if request.headers.get('Authorization', None) else False
        request_url = request.url
        begin_at = time.time()
        result = await call_next(request)
        end_at = time.time()
        mills = end_at - begin_at
        print(f'log middleware: url:{request_url}-是否授权:{is_auth}-耗时:{mills}-响应:{result}')
        print('log middleware end')
        return result

class CircuitMiddleware(BaseHTTPMiddleware):
    # 存储结构: {key: {"count": 次数, "expire_at": 过期时间戳}}
    circuit_map = {}

    # 配置
    THRESHOLD = 100  # 请求次数阈值
    WINDOW_SECONDS = 60  # 时间窗口（秒）

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        print('circuit middleware begin')
        client_ip = request.client.host
        path = request.url.path
        key = f"{client_ip}:{path}"

        now = time.time()

        # 检查并清理过期数据
        if key in self.circuit_map:
            record = self.circuit_map[key]
            if now > record["expire_at"]:
                # 已过期，重置计数
                self.circuit_map[key] = {"count": 1, "expire_at": now + self.WINDOW_SECONDS}
            else:
                # 未过期，累加计数
                record["count"] += 1
        else:
            # 新 key，初始化
            self.circuit_map[key] = {"count": 1, "expire_at": now + self.WINDOW_SECONDS}

        # 判断是否熔断
        if self.circuit_map[key]["count"] > self.THRESHOLD:
            return Response(content="Too Many Requests", status_code=429)
        response = await call_next(request)
        print('circuit middleware end')
        return response
