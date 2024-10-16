Test settings are in `pytest.ini` file.
```
pytest -vv --showlocals --cov=demo_service/ --cov-report=term-missing
```

tests:
1. `test/conftest.py`:
   This file will contain all the fixtures used across multiple test files.

2. `test/test_user_registration.py`:
   Tests related to user registration.

3. `test/test_user_retrieval.py`:
   Tests related to getting user information.

4. `test/test_user_promotion.py`:
   Tests related to promoting users to admin.
