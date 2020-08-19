import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from pydantic import BaseModel

from config import PSQL_CREDS


class Indicator(BaseModel):
    name: str


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


def make_connection():
    connection = psycopg2.connect(PSQL_CREDS)
    return connection


@app.get("/tracking-progress/v1/indicators")
def get_indicators():
    """Return list of all indicators that have been updated in past 30 days."""

    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)

    conn = make_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM updates WHERE updated >= %s", [one_month_ago])
    except psycopg2.Error as e:
        return JSONResponse(status_code=400, content={"message": "Database error: " + str(e)})

    results = cur.fetchall()
    conn.close()

    if not results:
        return []

    indicators = []
    for row in results:
        indicators.append(row[1])

    indicators = list(set(indicators))

    return indicators


@app.post("/tracking-progress/v1/indicators")
def add_indicator(indicator: Indicator) -> JSONResponse:
    """Add updated indicator."""

    conn = make_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO updates (indicator) VALUES (%s)", [indicator.name])
    except psycopg2.Error as e:
        return JSONResponse(status_code=400, content={"message": "Database error: " + str(e)})

    if cur.statusmessage != "INSERT 0 1":
        return JSONResponse(
            status_code=400, content={"message": "Error inserting indicator, contact developer."},
        )
    conn.commit()
    conn.close()
    return JSONResponse(status_code=200, content={"message": "success"})
