from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def print_resp(r, label):
    print(label, r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

# admin login
login_resp = client.post('/auth/login', data={'username':'admin@example.com','password':'admin123'})
print_resp(login_resp, 'Login')
if login_resp.status_code != 200:
    raise SystemExit('Login failed')

token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# create category
cat_resp = client.post('/categories/', json={'name':'Electronics'}, headers=headers)
print_resp(cat_resp, 'Create Category')
cat_id = cat_resp.json().get('id') if cat_resp.status_code == 200 else None

# create product (no image field as schema doesn't include it)
product_data = {
    'name': 'Phone',
    'description': 'Test phone',
    'price': 199.99,
    'stock': 5,
    'category_id': cat_id
}
prod_resp = client.post('/products/', json=product_data, headers=headers)
print_resp(prod_resp, 'Create Product')
