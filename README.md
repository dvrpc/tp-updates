# Tracking Progress Updates

Add an overlay to [Tracking Progress](https://github.com/dvrpc/TrackingProgress) indicator tiles to let users know they have recently been updated with new data. Indicators expire after 30 days.

The API code lives in the root directory, while the code for the front-end form is within the Form/ directory.

## Making Updates

See instructions on the front-end form.

## API

This is a FastAPI API. See docs at http://linux2.dvrpc.org/tracking-progress/v1/docs#/ (intranet).

### Tests

The tests use their own database, tracking_progress_updates_tests. They require a connection string in the variable PSQL_CREDS_TEST_DB in a config.py file in this directory. The connection string should include host, port, user, password, and dbname. After creating the database, run `psql -f create_tables.sql -d tracking_progress_updates_tests` to create the one table in the database. The tests create and delete records in the database each time they are run.

To run the tests, create/activate a virtual environment and run `python -m pytest tests.py`.
