import datetime
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_conn():
    """Connect to database, yield it, close it."""
    conn = psycopg2.connect(PSQL_CREDS)
    yield conn
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
