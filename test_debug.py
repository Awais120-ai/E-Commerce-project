# test_debug.py

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def print_resp(r):
    try:
        print(r.status_code, r.json())
    except Exception:
        print(r.status_code, r.text)

# 1. Register a new user
user_data = {"full_name": "Test User", "email": "test@example.com", "password": "password123"}
resp = client.post("/auth/register", json=user_data)
print("Register:")
print_resp(resp)

# 2. Login to get token
login_data = {"username": "test@example.com", "password": "password123"}
resp = client.post("/auth/login", data=login_data)
print("Login:")
print_resp(resp)
if resp.status_code != 200:
    token = None
else:
    token = resp.json().get("access_token")

headers = {"Authorization": f"Bearer {token}"} if token else {}

# Create Address
address_data = {
    "full_name": "Test User Address",
    "phone": "1234567890",
    "country": "TestCountry",
    "city": "TestCity",
    "postal_code": "12345",
    "address": "123 Test St"
}
resp = client.post("/addresses/", json=address_data, headers=headers)
print("Create Address:")
print_resp(resp)
address_id = resp.json().get("id") if resp.status_code == 200 else None

# 3. Create a category
category_data = {"name": "Electronics"}
resp = client.post("/categories/", json=category_data, headers=headers)
print("Create Category:")
print_resp(resp)
category_id = resp.json().get("id") if resp.status_code == 200 else None

# 4. Create a product
product_data = {"name": "Smartphone", "description": "A test phone", "price": 199.99, "stock": 10, "category_id": category_id, "image": "phone.jpg"}
resp = client.post("/products/", json=product_data, headers=headers)
print("Create Product:")
print_resp(resp)
product_id = resp.json().get("id") if resp.status_code == 200 else None

# 5. Add to cart
cart_data = {"product_id": product_id, "quantity": 2}
resp = client.post("/cart/", json=cart_data, headers=headers)
print("Add to Cart:")
print_resp(resp)
cart_id = resp.json().get("id") if resp.status_code == 200 else None

# 5b. Update Cart - Increase Quantity
if cart_id:
    update_data = {"quantity": 5}
    resp = client.put(f"/cart/{cart_id}", json=update_data, headers=headers)
    print("Update Cart (Increase to 5):")
    print_resp(resp)

# 5c. Update Cart - Decrease Quantity
if cart_id:
    update_data = {"quantity": 3}
    resp = client.put(f"/cart/{cart_id}", json=update_data, headers=headers)
    print("Update Cart (Decrease to 3):")
    print_resp(resp)

# 6. Create order (Checkout)
if address_id:
    checkout_data = {
        "address_id": address_id,
        "payment_method": "Credit Card"
    }
    resp = client.post("/orders/", json=checkout_data, headers=headers)
    print("Create Order (Checkout):")
    print_resp(resp)

# 7. List orders
resp = client.get("/orders/", headers=headers)
print("List Orders:")
print_resp(resp)

# 8. Get a specific order if available
if resp.status_code == 200 and isinstance(resp.json(), list) and resp.json():
    order_id = resp.json()[0]["id"]
    resp = client.get(f"/orders/{order_id}", headers=headers)
    print("Get Order:")
    print_resp(resp)

# 9. Test Buy Now Support
if address_id and product_id:
    buy_now_data = {
        "address_id": address_id,
        "payment_method": "Credit Card",
        "buy_now": True,
        "product_id": product_id,
        "quantity": 2
    }
    print("Testing Buy Now:")
    resp = client.post("/orders/", json=buy_now_data, headers=headers)
    print_resp(resp)

