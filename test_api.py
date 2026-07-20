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
            err_data = e.reason
        return e.code, err_data
    except Exception as e:
        return 0, str(e)

def test_flow():
    print("1. Testing root...")
    status, res = send_request(f"{BASE_URL}/")
    print(f"Status: {status}, Response: {res}")
    
    print("\n2. Testing get products (should be empty or some products)...")
    status, res = send_request(f"{BASE_URL}/products/")
    print(f"Status: {status}, Response: {res}")
    
    print("\n3. Testing user creation...")
    user_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "mypassword"
    }
    status, res = send_request(f"{BASE_URL}/users", method="POST", data=user_data)
    print(f"Status: {status}, Response: {res}")
    
    print("\n4. Testing login...")
    login_data = "username=test@example.com&password=mypassword".encode("utf-8")
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    status, login_res = send_request(f"{BASE_URL}/auth/login", method="POST", data=login_data, headers=headers)
    print(f"Status: {status}, Response: {login_res}")
    
    if status == 200:
        token = login_res["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n5. Testing get current user...")
        status, res = send_request(f"{BASE_URL}/users/me", headers=headers)
        print(f"Status: {status}, Response: {res}")

        # Test creating an address
        print("\n5.1. Testing create address...")
        address_data = {
            "address_type": "Home",
            "street_address": "123 Main St",
            "city": "Lahore",
            "state": "Punjab",
            "postal_code": "54000",
            "country": "Pakistan",
            "phone_number": "03001234567"
        }
        status, addr_res = send_request(f"{BASE_URL}/addresses/", method="POST", data=address_data, headers=headers)
        print(f"Status: {status}, Response: {addr_res}")

        # Test getting, updating, and deleting addresses
        if status == 201:
            addr_id = addr_res["id"]
            print("\n5.2. Testing get addresses...")
            status, res = send_request(f"{BASE_URL}/addresses/", headers=headers)
            print(f"Status: {status}, Response: {res}")

            print("\n5.3. Testing update address...")
            update_data = {
                "street_address": "456 New St"
            }
            status, res = send_request(f"{BASE_URL}/addresses/{addr_id}", method="PUT", data=update_data, headers=headers)
            print(f"Status: {status}, Response: {res}")

            print("\n5.4. Testing delete address...")
            status, res = send_request(f"{BASE_URL}/addresses/{addr_id}", method="DELETE", headers=headers)
            print(f"Status: {status}, Response: {res}")
    else:
        print("Login failed, skipping authenticated routes.")
        
    print("\n6. Testing create product...")
    product_data = {
        "name": "Widget",
        "description": "A very useful widget",
        "price": 19.99,
        "stock": 100
    }
    status, prod_res = send_request(f"{BASE_URL}/products/", method="POST", data=product_data)
    print(f"Status: {status}, Response: {prod_res}")

if __name__ == "__main__":
    test_flow()
