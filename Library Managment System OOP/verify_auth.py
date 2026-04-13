import requests
import os
import sqlite3

# URL of the running app
BASE_URL = "http://127.0.0.1:5000"

def reset_db():
    if os.path.exists('library.db'):
        os.remove('library.db')
    # trigger init_db by importing
    # But we can't easily import app.py here if it runs app.run() on import (which it does if name==main)
    # So we will rely on the app running in a separate process or just manual db check.
    # Actually, we can just connect and delete users.
    conn = sqlite3.connect('library.db')
    conn.execute('DROP TABLE IF EXISTS users')
    # Re-create is done by app on start.
    conn.close()

def test_auth():
    session = requests.Session()

    # 1. Register
    print("Testing Registration...")
    reg_data = {
        'fullname': 'Test User',
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'password123',
        'confirm-password': 'password123'
    }
    response = session.post(f"{BASE_URL}/register", data=reg_data, allow_redirects=False)
    
    if response.status_code == 302 and response.headers['Location'] == '/':
        print("PASS: Registration redirected to login.")
    else:
        print(f"FAIL: Registration failed. Status: {response.status_code}, Location: {response.headers.get('Location')}")
        return

    # 2. Verify DB
    conn = sqlite3.connect('library.db')
    user = conn.execute("SELECT * FROM users WHERE username='testuser'").fetchone()
    conn.close()
    if user:
        print("PASS: User found in database.")
    else:
        print("FAIL: User not found in database.")
        return

    # 3. Login
    print("Testing Login...")
    login_data = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = session.post(f"{BASE_URL}/", data=login_data, allow_redirects=False)
    
    if response.status_code == 302 and (response.headers['Location'] == '/dashboard' or response.headers['Location'].endswith('dashboard')):
        print("PASS: Login redirected to dashboard.")
    else:
        print(f"FAIL: Login failed. Status: {response.status_code}, Location: {response.headers.get('Location')}")
        # print body if fail
        # print(response.text)
        return

    # 4. Access Dashboard
    print("Testing Dashboard Access...")
    response = session.get(f"{BASE_URL}/dashboard", allow_redirects=False)
    if response.status_code == 200:
        print("PASS: Dashboard accessed successfully.")
        if "Welcome back" in response.text or "User" in response.text: # "Welcome back, User!" matches template
             print("PASS: Dashboard content seems correct.")
    else:
        print(f"FAIL: Dashboard access failed. Status: {response.status_code}")

    # 5. Logout
    print("Testing Logout...")
    response = session.get(f"{BASE_URL}/logout", allow_redirects=False)
    if response.status_code == 302 and response.headers['Location'] == '/':
        print("PASS: Logout redirected to login.")
    else:
        print(f"FAIL: Logout failed. Status: {response.status_code}, Location: {response.headers.get('Location')}")

    # 6. Access Dashboard after logout
    response = session.get(f"{BASE_URL}/dashboard", allow_redirects=False)
    if response.status_code == 302 and response.headers['Location'] == '/':
        print("PASS: Dashboard access after logout redirected to login.")
    else:
        print(f"FAIL: Dashboard access after logout did not redirect. Status: {response.status_code}")

if __name__ == "__main__":
    test_auth()
