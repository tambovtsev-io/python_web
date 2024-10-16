Test settings are in `pytest.ini` file. It is configured to run
```
pytest -vv --showlocals --cov=demo_service/ --cov-report=term-missing
```

tests:
1. `test/conftest.py`:
   Fixtures.

2. `test/test_user_registration.py`:
   Tests related to user registration.

3. `test/test_user_retrieval.py`:
   Tests related to getting user information.

4. `test/test_user_promotion.py`:
   Tests related to promoting users to admin.
