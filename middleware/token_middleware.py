import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

SECRET_KEY = "87f2c2be95c484df33a2a438a8a0284bd0cf79d8497d1b53e20f3ba9162b5e6e"

# Using static method for getting values

# class AuthenticationMiddleware:
#
#     @staticmethod
#     def authMiddle(request, response):
#         token = request.cookies.get("token")
#         if token == None :
#             response = RedirectResponse(url='/login')
#             return response
#         decoded = jwt.decode(token, SECRET_KEY, algorithms="HS256")
#         print(decoded)
#         username = decoded["emailID"]
#         return username


class TestMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        urls = ["/dashboard"]
        if request.url.path in urls:
            token = request.cookies.get("token")
            if token is None:
                response = RedirectResponse(url='/login')
                return response
            decoded = jwt.decode(token, SECRET_KEY, algorithms="HS256")
            print(decoded)
            username = decoded["emailID"]
            request.state.username = username
            print(f'inside {request.url.path} ')
            print(request)
            # response = await call_next(request)
            # return response

        response = await call_next(request)
        return response
