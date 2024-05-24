from uuid import uuid4

import pytest


@pytest.fixture
def user_id_1():
    return uuid4()


@pytest.fixture
def user_id_2():
    return uuid4()
