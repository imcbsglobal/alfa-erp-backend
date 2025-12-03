"""
Test script to verify login API returns menu structure
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login(email, password):
    """Test login and retrieve menu structure"""
    print(f"\n{'='*60}")
    print(f"Testing login for: {email}")
    print('='*60)
    
    url = f"{BASE_URL}/api/accounts/login/"
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract data
            if 'data' in data:
                user_data = data['data'].get('user', {})
                menus = data['data'].get('menus', [])
                role = data['data'].get('role', {})
                
                print("\n✓ Login Successful!")
                print(f"\nUser Information:")
                print(f"  - Name: {user_data.get('full_name')}")
                print(f"  - Email: {user_data.get('email')}")
                print(f"  - Primary Role: {user_data.get('primary_role')}")
                print(f"  - Is Staff: {user_data.get('is_staff')}")
                
                print(f"\nRole Information:")
                print(f"  - Name: {role.get('name')}")
                print(f"  - Code: {role.get('code')}")
                print(f"  - Description: {role.get('description')}")
                
                print(f"\nMenu Structure ({len(menus)} top-level menus):")
                for menu in menus:
                    print(f"  📁 {menu.get('label')} ({menu.get('path') or 'No path'})")
                    if menu.get('children'):
                        for child in menu['children']:
                            print(f"     └─ {child.get('label')} ({child.get('path') or 'No path'})")
                
                print(f"\n✓ Tokens received:")
                print(f"  - Access Token: {data['data'].get('access')[:30]}...")
                print(f"  - Refresh Token: {data['data'].get('refresh')[:30]}...")
                
            else:
                print("\n✗ Unexpected response format")
                print(json.dumps(data, indent=2))
        else:
            print(f"\n✗ Login Failed (Status {response.status_code})")
            print(json.dumps(response.json(), indent=2))
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ALFA ERP - Menu-Based RBAC Login Test")
    print("="*60)
    
    # Test with admin user
    test_login("admin@gmail.com", "admin123")
    
    # Test with regular user
    test_login("test@gmail.com", "test123")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60 + "\n")
