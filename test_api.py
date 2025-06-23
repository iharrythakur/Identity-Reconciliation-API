import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_identify_endpoint():
    """Test the /identify endpoint with various scenarios"""

    print("Testing BiteSpeed Identity Reconciliation API")
    print("=" * 50)

    # Test 1: Create first contact
    print("\n1. Creating first contact with email only...")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "foo@bar.com"
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Create second contact with phone only
    print("\n2. Creating second contact with phone only...")
    response = requests.post(f"{BASE_URL}/identify", json={
        "phoneNumber": "+919999999999"
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Link existing contacts by providing both email and phone
    print("\n3. Linking existing contacts by providing both email and phone...")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "foo@bar.com",
        "phoneNumber": "+919999999999"
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 4: Add new email to existing contact
    print("\n4. Adding new email to existing contact...")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "newemail@example.com",
        "phoneNumber": "+919999999999"
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 5: Add new phone to existing contact
    print("\n5. Adding new phone to existing contact...")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "foo@bar.com",
        "phoneNumber": "+918888888888"
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 6: Create completely new contact
    print("\n6. Creating completely new contact...")
    response = requests.post(f"{BASE_URL}/identify", json={
        "email": "different@example.com",
        "phoneNumber": "+917777777777"
    })
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 7: Test with no parameters (should fail)
    print("\n7. Testing with no parameters (should fail)...")
    try:
        response = requests.post(f"{BASE_URL}/identify", json={})
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Expected error: {e}")


if __name__ == "__main__":
    # Wait a bit for the server to start
    print("Waiting for server to start...")
    time.sleep(3)

    try:
        test_identify_endpoint()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")
