from fastapi.testclient import TestClient
import aval_backend as backend

# Mock enqueue_op
backend.enqueue_op = lambda op, timeout=5.0: {
    'Code': 'ms01', 'Company': 'Microsoft', 'Continent': 'Asia',
    'Country': 'India', 'State': 'Telangana', 'Sector': 'Technology',
    'SubSector': 'Cloud Computing', 'Employees': 12000
}

client = TestClient(backend.app)

endpoints = ['/', '/sample', '/sample/many/3', '/branches/Microsoft']
for ep in endpoints:
    r = client.get(ep)
    print(ep, '->', r.status_code)
    try:
        print(r.json())
    except Exception:
        print('No JSON')
