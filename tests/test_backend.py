import sys
import os
import pytest
from fastapi.testclient import TestClient

# make sure project root is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import aval_backend as backend


@pytest.fixture(autouse=True)
def mock_qsharp_calls(monkeypatch):
    # Mock enqueue_op to return a deterministic branch without requiring Q#
    def fake_enqueue(op: str, timeout: float = 5.0):
        return {
            'Code': 'ms01', 'Company': 'Microsoft', 'Continent': 'Asia',
            'Country': 'India', 'State': 'Telangana', 'Sector': 'Technology',
            'SubSector': 'Cloud Computing', 'Employees': 12000
        }

    monkeypatch.setattr(backend, 'enqueue_op', lambda op, timeout=5.0: fake_enqueue(op, timeout))
    yield


def test_health():
    client = TestClient(backend.app)
    r = client.get('/')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_sample_one():
    client = TestClient(backend.app)
    r = client.get('/sample')
    assert r.status_code == 200
    body = r.json()
    assert body['company'] == 'Microsoft'
    assert body['code'] == 'ms01'


def test_sample_many():
    client = TestClient(backend.app)
    r = client.get('/sample/many/3')
    assert r.status_code == 200
    body = r.json()
    assert 'samples' in body and 'distribution' in body
    assert len(body['samples']) == 3


def test_branches_for_company():
    client = TestClient(backend.app)
    r = client.get('/branches/Microsoft')
    assert r.status_code == 200
    body = r.json()
    assert len(body) > 0
    assert body[0]['company'] == 'Microsoft'
    assert body[0]['continent'] != 'unknown'
