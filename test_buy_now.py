import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def send_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None and not isinstance(data, (str, bytes)):
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_data = e.read().decode("utf-8")
        return e.code, err_data
    except Exception as e:
        return 0, str(e)

def setup_and_test():
    # 1. Login user
    login_data = "username=test@example.com&password=mypassword".encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    status, login_res = send_request(f"{BASE_URL}/auth/login", method="POST", data=login_data, headers=headers)
    
    if status != 200:
        # Create user first
        user_data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "mypassword"
        }
        send_request(f"{BASE_URL}/users", method="POST", data=user_data)
        status, login_res = send_request(f"{BASE_URL}/auth/login", method="POST", data=login_data, headers=headers)
        
    token = login_res["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # Clean existing cart
    status, cart_items = send_request(f"{BASE_URL}/cart/", headers=auth_headers)
    print("Initial Cart items:", cart_items)
    for item in cart_items:
        send_request(f"{BASE_URL}/cart/{item['id']}", method="DELETE", headers=auth_headers)
    print("Cleared cart.")

    # Create two test products
    # Product A
    prod_a_data = {"name": "Product A", "description": "Desc A", "price": 10.0, "stock": 10}
    status, prod_a = send_request(f"{BASE_URL}/products/", method="POST", data=prod_a_data, headers=auth_headers)
    print("Created Product A:", prod_a)
    
    # Product B
    prod_b_data = {"name": "Product B", "description": "Desc B", "price": 20.0, "stock": 15}
    status, prod_b = send_request(f"{BASE_URL}/products/", method="POST", data=prod_b_data, headers=auth_headers)
    print("Created Product B:", prod_b)

    prod_a_id = prod_a["id"]
    prod_b_id = prod_b["id"]

    # --- Scenario 3: Cart is empty, click Order Now on Product A ---
    print("\n--- Testing Scenario 3: Cart is empty, Order Now Product A ---")
    # Get current stock of A
    status, p_a_before = send_request(f"{BASE_URL}/products/{prod_a_id}")
    print(f"Product A stock before: {p_a_before['stock']}")

    buy_now_data = {"product_id": prod_a_id, "quantity": 1}
    status, order_res = send_request(f"{BASE_URL}/orders/buy-now", method="POST", data=buy_now_data, headers=auth_headers)
    print("Buy Now response:", status, order_res)

    status, p_a_after = send_request(f"{BASE_URL}/products/{prod_a_id}")
    print(f"Product A stock after: {p_a_after['stock']}")
    
    status, cart_after = send_request(f"{BASE_URL}/cart/", headers=auth_headers)
    print("Cart after Scenario 3:", cart_after)

    # --- Scenario 2: Cart contains only Product B, Order Now on Product A ---
    print("\n--- Testing Scenario 2: Cart has only Product B, Order Now Product A ---")
    # Add Product B to cart
    status, cart_b = send_request(f"{BASE_URL}/cart/", method="POST", data={"product_id": prod_b_id, "quantity": 2}, headers=auth_headers)
    print("Added B to cart:", cart_b)
    
    status, p_b_before = send_request(f"{BASE_URL}/products/{prod_b_id}")
    status, p_a_before = send_request(f"{BASE_URL}/products/{prod_a_id}")
    print(f"Product A stock before: {p_a_before['stock']}, Product B stock before: {p_b_before['stock']}")

    status, cart_now = send_request(f"{BASE_URL}/cart/", headers=auth_headers)
    print("Cart before Scenario 2:", cart_now)

    buy_now_data = {"product_id": prod_a_id, "quantity": 1}
    status, order_res = send_request(f"{BASE_URL}/orders/buy-now", method="POST", data=buy_now_data, headers=auth_headers)
    print("Buy Now response:", status, order_res)

    status, p_a_after = send_request(f"{BASE_URL}/products/{prod_a_id}")
    status, p_b_after = send_request(f"{BASE_URL}/products/{prod_b_id}")
    print(f"Product A stock after: {p_a_after['stock']}, Product B stock after: {p_b_after['stock']}")

    status, cart_after = send_request(f"{BASE_URL}/cart/", headers=auth_headers)
    print("Cart after Scenario 2:", cart_after)

    # --- Scenario 1: Cart has Product A and Product B, Order Now on Product A ---
    print("\n--- Testing Scenario 1: Cart has A and B, Order Now Product A ---")
    # Add Product A to cart (it's already cleared or not in cart, but let's make sure both are in cart)
    # Clear cart first
    for item in cart_after:
        send_request(f"{BASE_URL}/cart/{item['id']}", method="DELETE", headers=auth_headers)
    
    # Add A to cart
    status, cart_a = send_request(f"{BASE_URL}/cart/", method="POST", data={"product_id": prod_a_id, "quantity": 2}, headers=auth_headers)
    # Add B to cart
    status, cart_b = send_request(f"{BASE_URL}/cart/", method="POST", data={"product_id": prod_b_id, "quantity": 3}, headers=auth_headers)
    
    status, p_a_before = send_request(f"{BASE_URL}/products/{prod_a_id}")
    status, p_b_before = send_request(f"{BASE_URL}/products/{prod_b_id}")
    print(f"Product A stock before: {p_a_before['stock']}, Product B stock before: {p_b_before['stock']}")
    
    status, cart_now = send_request(f"{BASE_URL}/cart/", headers=auth_headers)
    print("Cart before Scenario 1:", cart_now)

    buy_now_data = {"product_id": prod_a_id, "quantity": 1}
    status, order_res = send_request(f"{BASE_URL}/orders/buy-now", method="POST", data=buy_now_data, headers=auth_headers)
    print("Buy Now response:", status, order_res)

    status, p_a_after = send_request(f"{BASE_URL}/products/{prod_a_id}")
    status, p_b_after = send_request(f"{BASE_URL}/products/{prod_b_id}")
    print(f"Product A stock after: {p_a_after['stock']}, Product B stock after: {p_b_after['stock']}")

    status, cart_after = send_request(f"{BASE_URL}/cart/", headers=auth_headers)
    print("Cart after Scenario 1:", cart_after)

if __name__ == "__main__":
    setup_and_test()
