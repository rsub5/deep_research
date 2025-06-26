import secrets
import json
import os
from cryptography.fernet import Fernet

TOKEN_FILE = "tokens.json"

FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise ValueError('FERNET_KEY not set in environment')
fernet = Fernet(FERNET_KEY.encode())

def generate_token(length=16):
    """Generate a secure random token."""
    return secrets.token_hex(length)

def save_token(email, token, filename=TOKEN_FILE):
    tokens = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            tokens = json.load(f)
    try:
        encrypted_token = fernet.encrypt(token.encode()).decode()
        tokens[email] = encrypted_token
        with open(filename, "w") as f:
            json.dump(tokens, f)
    except Exception as e:
        print(f"[ERROR] Failed to save token for {email}: {e}")

def get_token(email, filename=TOKEN_FILE):
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        tokens = json.load(f)
    encrypted_token = tokens.get(email)
    if not encrypted_token:
        return None
    try:
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception:
        return None

def validate_token(email, token, filename=TOKEN_FILE):
    return get_token(email, filename) == token

if __name__ == "__main__":
    email = input("Enter email: ").strip()
    token = generate_token()
    save_token(email, token)
    print(f"Token for {email}: {token}") 