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
import psycopg2
from pydantic import BaseModel

from config import PSQL_CREDS


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
    allow_origins=["http://localhost", "http://intranet.dvrpc.org"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


def get_conn():
    """Connect to database, yield it, close it."""
    conn = psycopg2.connect(PSQL_CREDS)
    try:
        yield conn
    finally:
        conn.close()


@app.get(
    "/tracking-progress/v1/indicators",
    responses={500: {"model": Message, "description": "Internal Server Error"}},
)
def get_indicators(conn=Depends(get_conn)):
    """Return list of all indicators that have been updated in past 30 days."""
    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM updates WHERE updated >= %s", [one_month_ago])
    except psycopg2.Error as e:
        return JSONResponse(status_code=500, content={"message": "Database error: " + str(e)})

    results = cur.fetchall()

    if not results:
        return []

    indicators = []
    for row in results:
        indicators.append(row[1])

    indicators = list(set(indicators))

    return indicators


@app.post(
    "/tracking-progress/v1/indicators",
    responses={500: {"model": Message, "description": "Internal Server Error"}},
    status_code=201,
)
def add_indicator(indicator: Indicator, conn=Depends(get_conn)):
    """Add updated indicator."""
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO updates (indicator) VALUES (%s)", [indicator.name])
    except psycopg2.Error as e:
        return JSONResponse(status_code=500, content={"message": "Database error: " + str(e)})

    if cur.statusmessage != "INSERT 0 1":
        return JSONResponse(
            status_code=500, content={"message": "Error inserting indicator, contact developer."}
        )
    conn.commit()
    return {"message": "success"}


@app.delete(
    "/tracking-progress/v1/indicators",
    responses={
        404: {"model": Message, "description": "Not Found"},
        500: {"model": Message, "description": "Internal Server Error"},
    },
    status_code=200,
)
def delete_indicator(indicator: Indicator, conn=Depends(get_conn)):
    """Delete an updated indicator (in case one was mistakenly added)."""
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM updates WHERE indicator = %s", [indicator.name])
    except psycopg2.Error as e:
        return JSONResponse(status_code=500, content={"message": "Database error: " + str(e)})

    if "DELETE" in cur.statusmessage:
        if cur.statusmessage == "DELETE 0":
            return JSONResponse(
                status_code=404,
                content={"message": "No indicator with that name found; not deleted."},
            )
        conn.commit()
        return JSONResponse(status_code=200, content={"message": "success"})

    return JSONResponse(
        status_code=500, content={"message": "Error inserting indicator, contact developer."}
    )
