from fastapi.testclient import TestClient
from aval_backend import app

client = TestClient(app)

print('GET /sample-one')
resp = client.get('/sample-one')
print('status', resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('Error decoding JSON:', e)
    print('Text:', resp.text)

print('\nGET /sample-many?count=5')
resp = client.get('/sample-many?count=5')
print('status', resp.status_code)
print(resp.text)

print('\nGET /branches')
resp = client.get('/branches')
print('status', resp.status_code)
print(resp.text)
