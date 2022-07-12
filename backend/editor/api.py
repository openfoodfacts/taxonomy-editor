from datetime import datetime

# FastAPI
from fastapi import FastAPI, status, Response, Depends, Header, HTTPException, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Open Food Facts Taxonomy Editor API")

# Allow anyone to call the API from their own apps
app.add_middleware(
    CORSMiddleware,
    # FastAPI doc related to allow_origin (to avoid CORS issues):
    # "It's also possible to declare the list as "*" (a "wildcard") to say that all are allowed.
    # But that will only allow certain types of communication, excluding everything that involves 
    # credentials: Cookies, Authorization headers like those used with Bearer Tokens, etc.
    # So, for everything to work correctly, it's better to specify explicitly the allowed origins."
    # => Workarround: use allow_origin_regex
    # Source: https://github.com/tiangolo/fastapi/issues/133#issuecomment-646985050
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
    return {"message": "Hello user! Tip: open /docs or /redoc for documentation"}

@app.get("/ping")
async def pong(response: Response):
    """
    Check server health
    """
    pong = datetime.now()
    return {"ping": "pong @ %s" % pong}