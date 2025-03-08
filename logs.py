import json
import httpx
import traceback
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from conf import SERVER_ID, SAVE_LOG_URL, LOG_SECRET


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.body = None  # Инициализация

        try:
            # Читаем тело запроса один раз
            body_bytes = await request.body()
            request.state.body = body_bytes.decode("utf-8")
        except Exception:
            request.state.body = "Failed to read body"

        try:
            response = await call_next(request)
        except Exception as e:
            # Генерируем traceback ошибки
            tb_str = "".join(traceback.format_exception(None, e, e.__traceback__))
            last_500_chars = tb_str[-500:]

            log_data = {
                "service_name": f"file server{SERVER_ID}",
                "level": 4,
                "method": request.method,
                "url": str(request.url),
                "status_code": 500,
                "client_ip": request.client.host,
                "headers": dict(request.headers),
                "body": request.state.body,  # Берём сохранённое тело запроса
                "error_traceback": last_500_chars,  # Сохраняем traceback ошибки
            }

            # Асинхронно отправляем лог
            async with httpx.AsyncClient() as client:
                await client.post(SAVE_LOG_URL, json=log_data, headers={'SECRET': LOG_SECRET})

            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        # Логируем ошибки 4xx и 5xx
        if response.status_code >= 200:
            log_data = {
                "service_name": f"file server{SERVER_ID}",
                "level": 4 if response.status_code >= 400 else 1,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "client_ip": request.client.host,
                "headers": dict(request.headers),
                "body": request.state.body,  # Используем сохранённое тело запроса
            }

            async with httpx.AsyncClient() as client:
                await client.post(SAVE_LOG_URL, json=log_data, headers={'SECRET': LOG_SECRET})

        return response
