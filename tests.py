"""
Testing the endpoints.
Note that this requires the db referenced in PG_CREDS_TEST_DB to be set up separately.
"""
import datetime

from fastapi.testclient import TestClient
import psycopg
import pytest

from config import PG_CREDS_TEST_DB
from main import app, db

ENDPOINT = "/tracking-progress/v1/indicators"


def test_db():
    """Provide a connection to the test db.

    Each endpoint uses a db connection as a depenency. For testing, that db dependency is
    overwritten with this one, through the app.dependency statement below.

    The primary use of this is to be able to examine db changes (that occur between the insertion
    and deletion of records made by the setup_test_db fixture) made by the tests.
    """
    return psycopg.connect(PG_CREDS_TEST_DB)


# use the test database for all tests
# See <https://fastapi.tiangolo.com/advanced/testing-dependencies/#use-the-appdependency_overrides-attribute>
app.dependency_overrides[db] = test_db


@pytest.fixture
def client():
    """Test app."""
    client = TestClient(app)
    return client


@pytest.fixture
def setup_test_db():
    """Insert and then delete records so we are always working with the same data."""
    conn = test_db()
    conn.execute("INSERT INTO updates (indicator) VALUES ('indicator1')")
    conn.execute("INSERT INTO updates (indicator) VALUES ('indicator2')")
    conn.execute("INSERT INTO updates (indicator) VALUES ('indicator3')")
    conn.execute("INSERT INTO updates (indicator) VALUES ('indicator4')")
    conn.execute("INSERT INTO updates (indicator) VALUES ('indicator5')")
    conn.execute("INSERT INTO updates (indicator) VALUES ('indicator6')")

    # update some of the indicators so that updated is more than 30 days ago
    two_months_ago = datetime.date.today() - datetime.timedelta(days=60)
    conn.execute("UPDATE updates SET updated = %s WHERE indicator = 'indicator4'", [two_months_ago])
    conn.execute("UPDATE updates SET updated = %s WHERE indicator = 'indicator5'", [two_months_ago])
    conn.execute("UPDATE updates SET updated = %s WHERE indicator = 'indicator6'", [two_months_ago])
    conn.commit()

    try:
        yield
    finally:
        conn.execute("DELETE FROM updates")
        conn.commit()
        conn.close()


def test_test_db(client, setup_test_db):
    """Check that we can connect to test db and that it is set up properly."""
    with test_db() as conn:
        results = conn.execute("SELECT * FROM updates").fetchall()

    indicators = {}
    for row in results:
        indicators[row[1]] = row[2]
    assert len(indicators) == 6
    assert indicators["indicator1"] == datetime.date.today()
    assert indicators["indicator4"] == datetime.date.today() - datetime.timedelta(days=60)


##############
# GET ENDPOINT


def test_get_success(client, setup_test_db):
    response = client.get(ENDPOINT)
    assert response.status_code == 200


def test_get_returns_list(client):
    response = client.get(ENDPOINT)
    data = response.json()
    assert isinstance(data, list)


def test_get_returns_correct_number_of_indicators(client, setup_test_db):
    response = client.get(ENDPOINT)
    data = response.json()
    assert len(data) == 3


###############
# POST ENDPOINT


def test_success_message_returned_after_adding_indicator(client, setup_test_db):
    response = client.post(ENDPOINT, json={"name": "indicator7"})
    data = response.json()
    assert data["message"] == "success"


def test_verify_indicator_added_to_db(client, setup_test_db):
    client.post(ENDPOINT, json={"name": "indicator7"})
    response = client.get(ENDPOINT)
    data = response.json()
    assert len(data) == 4


#################
# DELETE ENDPOINT


def test_success_message_after_deleting_indicator(client, setup_test_db):
    response_delete = client.delete(ENDPOINT, json={"name": "indicator1"})
    data_delete = response_delete.json()
    response_get = client.get(ENDPOINT)
    data_get = response_get.json()
    assert data_delete["message"] == "success"
    assert len(data_get) == 2


def test_attempt_deletion_of_indicator_not_in_db_returns_error_message(client, setup_test_db):
    response = client.delete(ENDPOINT, json={"name": "not a valid indicator name"})
    data = response.json()
    assert response.status_code == 404
    assert data["message"] == "No indicator with that name found; not deleted."
