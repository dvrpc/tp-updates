import datetime

from fastapi.testclient import TestClient
import psycopg2
import pytest

from config import PSQL_CREDS_TEST_DB
from main import app, get_conn

ENDPOINT = "/tracking-progress/v1/indicators"


@pytest.fixture
def client():
    client = TestClient(app)
    return client


def get_test_conn():
    """Set up testing database, yielding the connection.

    Note that this requires the db in PSQL_CREDS_TEST_DB to be set up separately.
    """
    conn = psycopg2.connect(PSQL_CREDS_TEST_DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO updates (indicator) VALUES ('indicator1')")
    cur.execute("INSERT INTO updates (indicator) VALUES ('indicator2')")
    cur.execute("INSERT INTO updates (indicator) VALUES ('indicator3')")
    cur.execute("INSERT INTO updates (indicator) VALUES ('indicator4')")
    cur.execute("INSERT INTO updates (indicator) VALUES ('indicator5')")
    cur.execute("INSERT INTO updates (indicator) VALUES ('indicator6')")

    # update some of the indicators so that updated is more than 30 days ago
    two_months_ago = datetime.date.today() - datetime.timedelta(days=60)
    cur.execute("UPDATE updates SET updated = %s WHERE indicator = 'indicator4'", [two_months_ago])
    cur.execute("UPDATE updates SET updated = %s WHERE indicator = 'indicator5'", [two_months_ago])
    cur.execute("UPDATE updates SET updated = %s WHERE indicator = 'indicator6'", [two_months_ago])

    yield conn

    conn.commit()
    conn.close()


def clear_db():
    conn = psycopg2.connect(PSQL_CREDS_TEST_DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM updates")
    conn.commit()
    conn.close()


# use the test database for all tests
# See <https://fastapi.tiangolo.com/advanced/testing-dependencies/#use-the-appdependency_overrides-attribute>
app.dependency_overrides[get_conn] = get_test_conn

##############
# GET ENDPOINT


def test_get_success(client):
    response = client.get(ENDPOINT)
    assert response.status_code == 200


def test_get_returns_list(client):
    response = client.get(ENDPOINT)
    data = response.json()
    assert isinstance(data, list)


def test_test_db_setup(client):
    """Check that we can connect to test db and that it is set up properly."""
    cur = next(get_test_conn()).cursor()  # get the conn out of generator, then the cursor
    cur.execute("SELECT * from updates")
    results = cur.fetchall()
    indicators = {}
    for row in results:
        indicators[row[1]] = row[2]
    assert len(indicators) == 6
    assert indicators["indicator1"] == datetime.date.today()
    assert indicators["indicator4"] == datetime.date.today() - datetime.timedelta(days=60)


def test_get_returns_correct_number_of_indicators(client):
    response = client.get(ENDPOINT)
    data = response.json()
    assert len(data) == 3


###############
# POST ENDPOINT

# all post tests need to clear the database afterwords, because it's not in the function for it
# since we sometimes want to then query the database to confirm insert


def test_success_message_returned_after_adding_indicator(client):
    response = client.post(ENDPOINT, json={"name": "indicator7"})
    data = response.json()
    clear_db()
    assert data["message"] == "success"


def test_verify_indicator_added_to_db(client):
    client.post(ENDPOINT, json={"name": "indicator7"})
    response = client.get(ENDPOINT)
    data = response.json()
    clear_db()
    assert len(data) == 4
