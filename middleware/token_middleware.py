import jwt
from fastapi import Request, FastAPI
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse, RedirectResponse, Response

app = FastAPI()

SECRET_KEY = "87f2c2be95c484df33a2a438a8a0284bd0cf79d8497d1b53e20f3ba9162b5e6e"


class AuthenticationMiddleware:

    @staticmethod
    def authMiddle(request, response):
        token = request.cookies.get("token")
        if token == None :
            response = RedirectResponse(url='/login')
            return response
        decoded = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        print(decoded)
        username = decoded["emailID"]
        return username


class TestMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next,):
        urls = ["/testing", "/"]
        if request.url.path in urls:
            token = request.cookies.get("token")
            if(token == None):
                response = RedirectResponse(url='/login')
                return response
            decoded = jwt.decode(token, SECRET_KEY, algorithms="HS256")
            print(decoded)
            username = decoded["emailID"]
            print(f'inside {request.url.path} ')
            print(request)
            response = await call_next(request)
            return response
        else:
            response = await call_next(request)
            return response


class TokenMiddleware(BaseHTTPMiddleware):

    def dispatch(self, request: Request, call_next):
        allowed_endpoint = ["/"]
        if request.url.path in allowed_endpoint:
            token = request.cookies.get("token")

            if token is None:
                return PlainTextResponse("No")

            try:

                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                username = payload["emailID"]
                # username = "Irish"
                emailid = username
                # return emailid
                #     request.app.state.username = username
                #     return request.app.state.username

            except jwt.DecodeError:
                return PlainTextResponse("Invalid")

        response = call_next(request)
        return response
        # allowed_endpoint = ["/login"]
        # # Excluded endpoints
        # excluded_endpoint = ['/docs', '/']
        # if request.url.path in allowed_endpoint:
        #     token = request.cookies.get("token")
        #     # response = await call_next(request)
        #     # return response
        #
        # if token is None:
        #     return PlainTextResponse("Unauthorized", status_code=401)
        #
        # try:
        #     secret_key = "b156066876b66942253b1c915b18ceb2e805ac44341694b1e5b6ed3673c37ccd"
        #     payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        #     username = payload["usrname"]
        #
        #     request.state.username = username
        # except jwt.DecodeError:
        #     return PlainTextResponse("Invalid Token", status_code=401)
        #
        # response = await call_next(request)
        # return response
