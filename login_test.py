from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.post('/auth/login', data={'username':'admin@example.com','password':'admin123'})
print('Status:', resp.status_code)
print('Response:', resp.json())
