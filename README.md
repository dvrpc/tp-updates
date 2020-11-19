# Tracking Progress Updates API

This API enables adding and removing updated [Tracking Progress](https://github.com/dvrpc/TrackingProgress) indicators, as well as getting those that have been updated in the past 30 days.

## Tests

The tests use their own database, tracking_progress_updates_tests. They require a connection string in the variable PSQL_CREDS_TEST_DB in a config.py file in this directory. The connection string should include host, port, user, password, and dbname. After creating the database, run `psql -f create_tables.sql -d tracking_progress_updates_tests` to create the one table in the database. The tests create and delete records in the database each time they are run.

To run the tests, create/activate a virtual environement and run `python -m pytest tests.py`.
