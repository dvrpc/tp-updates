"""
API for tracking updated indicators for Tracking Progress.

Front end form on the intranet enables adding and removing the names of indicators that have been
updated.

The GET endpoint returns a list of indicators updated in the past 30 days so the TP app can display
a UI element on the indicator to represent that.
"""
import datetime

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg
from pydantic import BaseModel

from config import PG_CREDS


class Indicator(BaseModel):
    name: str


class Message(BaseModel):
    message: str


app = FastAPI(
    title="Tracking Progress Updates API",
    openapi_url="/tracking-progress/v1/openapi.json",
    docs_url="/tracking-progress/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8013",
        "http://localhost",
        "http://intranet.dvrpc.org",
        "http://staging.dvrpc.org",
        "https://dvrpc.org",
        "https://www.dvrpc.org",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


def db():
    """
    Create connection to database.

    Using a function so that we can insert it as a dependency, and thus use a different
    database connection when testing.
    """
    return psycopg.connect(PG_CREDS)


@app.get(
    "/tracking-progress/v1/indicators",
    responses={500: {"model": Message, "description": "Internal Server Error"}},
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
    "/tracking-progress/v1/indicators",
    responses={500: {"model": Message, "description": "Internal Server Error"}},
    status_code=201,
)
def add_indicator(indicator: Indicator, db=Depends(db)):
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
    "/tracking-progress/v1/indicators",
    responses={
        404: {"model": Message, "description": "Not Found"},
        500: {"model": Message, "description": "Internal Server Error"},
    },
    status_code=200,
)
def delete_indicator(indicator: Indicator, db=Depends(db)):
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
        return JSONResponse(status_code=200, content={"message": "success"})

    return JSONResponse(
        status_code=500,
        content={"message": "Error inserting indicator, contact developer."},
    )
