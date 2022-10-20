# Tracking Progress Updates API

Get, add, or remove names of [Tracking Progress](https://github.com/dvrpc/TrackingProgress) indicators, so that an overlay can optionally be placed on the corresponding indicator tile to notify users when recent updates have been made. For the GET endpoint, only indicators added within the past 30 days will be returned.

See API docs at <http://linux3.dvrpc.org/api/tp-updates/v1/docs#/> (internal).

The frontend is handled by <https://github.com/dvrpc/tp-updater>.

### Tests

The tests use their own database, tracking_progress_updates_tests. They require a connection string in the variable PSQL_CREDS_TEST_DB in a config.py file in this directory. The connection string should include host, port, user, password, and dbname. After creating the database, run `psql -f create_tables.sql -d tracking_progress_updates_tests` to create the one table in the database. The tests create and delete records in the database each time they are run.

To run the tests, create/activate a virtual environment and run `python -m pytest tests.py`.
