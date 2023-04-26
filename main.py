"""
API for tracking updated indicators for Tracking Progress.

Front end form on the intranet enables adding and removing the names of indicators that have been
updated.

The GET endpoint returns a list of indicators updated in the past 30 days so the TP app can display
a UI element on the indicator to represent that.
"""
import datetime
from typing import List
from typing_extensions import Annotated
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import psycopg
from pydantic import BaseModel

from config import PG_CREDS, USERNAME, PASSWORD


class Indicator(BaseModel):
    name: str


class Message(BaseModel):
    message: str


PATH = "/api/tp-updates/v1"

app = FastAPI(
    title="Tracking Progress Updates API",
    openapi_url=PATH + "/openapi.json",
    docs_url=PATH + "/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://linux3.dvrpc.org",
        "http://intranet.dvrpc.org",
        "http://staging.dvrpc.org",
        "https://staging.dvrpc.org",
        "https://dvrpc.org",
        "https://www.dvrpc.org",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

security = HTTPBasic()


def basic_auth(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    """
    Create a simple verification method using Basic HTTP Authentication.
    In any HTTP request, use the Basic Auth Authorization header to provide a username and password,
    which will be validated against the environment variables in config.py.
    This fn can be used in an endpoint to add authentication to it. See the POST and DELETE
    endpoints below.
    """
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), USERNAME.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), PASSWORD.encode("utf8")
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return


def db():
    """
    Create connection to database.

    Using a function so that we can insert it as a dependency, and thus use a different
    database connection when testing.
    """
    return psycopg.connect(PG_CREDS)


@app.get(
    PATH + "/indicators",
    responses={500: {"model": Message, "description": "Internal Server Error"}},
    response_model=List[str],
)
def get_indicators(db=Depends(db)):
    """Return list of all indicators that have been updated in past 30 days."""
    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)

    try:
        with db as conn:
            results = conn.execute(
                "SELECT * FROM updates WHERE updated >= %s", [one_month_ago]
            ).fetchall()
    except psycopg.Error as e:
        return JSONResponse(status_code=500, content={"message": "Database error: " + str(e)})

    if not results:
        return []

    indicators = []
    for row in results:
        indicators.append(row[1])

    return list(set(indicators))


@app.post(
    PATH + "/indicators",
    responses={500: {"model": Message, "description": "Internal Server Error"}},
    status_code=201,
    response_model=Message,
)
def add_indicator(
    username: Annotated[str, Depends(basic_auth)], indicator: Indicator, db=Depends(db)
):
    """Add updated indicator."""
    try:
        with db as conn:
            cur = conn.execute("INSERT INTO updates (indicator) VALUES (%s)", [indicator.name])

    except psycopg.Error as e:
        return JSONResponse(status_code=500, content={"message": "Database error: " + str(e)})

    if cur.statusmessage != "INSERT 0 1":
        return JSONResponse(
            status_code=500,
            content={"message": "Error inserting indicator, contact developer."},
        )

    return {"message": "success"}


@app.delete(
    PATH + "/indicators",
    responses={
        404: {"model": Message, "description": "Not Found"},
        500: {"model": Message, "description": "Internal Server Error"},
    },
    response_model=Message,
)
def delete_indicator(
    username: Annotated[str, Depends(basic_auth)], indicator: Indicator, db=Depends(db)
):
    """Delete an updated indicator (in case one was mistakenly added)."""

    try:
        with db as conn:
            cur = conn.execute("DELETE FROM updates WHERE indicator = %s", [indicator.name])
    except psycopg.Error as e:
        return JSONResponse(status_code=500, content={"message": "Database error: " + str(e)})

    if "DELETE" in cur.statusmessage:
        if cur.statusmessage == "DELETE 0":
            return JSONResponse(
                status_code=404,
                content={"message": "No indicator with that name found; not deleted."},
            )
        return {"message": "success"}

    return JSONResponse(
        status_code=500,
        content={"message": "Error inserting indicator, contact developer."},
    )
