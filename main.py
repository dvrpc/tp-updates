import datetime
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

from config import PSQL_CREDS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_db_cursor():
    connection = psycopg2.connect(PSQL_CREDS)
    return connection.cursor()


@app.get("/indicators")
def get_indicators() -> List[str]:
    """Return list of all indicators that have been updated in past 30 days."""

    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)

    query = "SELECT * FROM updates WHERE updated >= %s"
    cur = get_db_cursor()
    cur.execute(query, [one_month_ago])
    results = cur.fetchall()

    if not results:
        return []

    indicators = []
    for row in results:
        indicators.append(row[1])

    indicators = list(set(indicators))

    return indicators


@app.post("/indicators")
def add_indicator(name: str):
    """Add updated indicator."""
    cur = get_db_cursor()
    pass
