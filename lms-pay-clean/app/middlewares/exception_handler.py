from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import sqlalchemy.exc

from app.setting.setting import logger

class ExceptionHandlerMiddlerware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ValueError as e:
            logger.error(f"Error: {e}")
            return JSONResponse(
                status_code=403,
                content=str(e)
            )
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f"Error: {e}")
            return JSONResponse(
                status_code=400,
                content=str(e).split("\n")[1]
            )
        