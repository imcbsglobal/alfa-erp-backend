import urllib.request
import json

# Test login
url = 'http://localhost:8000/api/auth/login/'
data = json.dumps({'email': 'admin@gmail.com', 'password': 'admin123'}).encode()
headers = {'Content-Type': 'application/json'}

req = urllib.request.Request(url, data=data, headers=headers)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())

print('✓ Login successful!')
print(f'\nUser: {result["data"]["user"]["email"]}')
print(f'Menus: {len(result["data"]["menus"])} items')
print('\nMenu Structure:')
for menu in result['data']['menus']:
    print(f'  📁 {menu["name"]} ({menu["url"]})')
    if menu.get('children'):
        for child in menu['children']:
            print(f'     └─ {child["name"]} ({child["url"]})')
