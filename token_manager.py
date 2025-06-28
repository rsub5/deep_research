import secrets
import json
import os
from cryptography.fernet import Fernet

TOKEN_FILE = "tokens.json"

FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise ValueError('FERNET_KEY not set in environment')
fernet = Fernet(FERNET_KEY.encode())

RESEARCH_RUN_COUNT_TOKEN = 2

def generate_token(length=16):
    """Generate a secure random token."""
    return secrets.token_hex(length)

def load_tokens(filename=TOKEN_FILE):
    if not os.path.exists(filename):
        return {}
    with open(filename, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception:
        return {}

def save_tokens(tokens, filename=TOKEN_FILE):
    data = json.dumps(tokens).encode()
    encrypted = fernet.encrypt(data)
    with open(filename, "wb") as f:
        f.write(encrypted)

def save_token(email, token, filename=TOKEN_FILE):
    tokens = load_tokens(filename)
    tokens[email] = {"token": token, "count": 0}
    save_tokens(tokens, filename)

def get_token(email, filename=TOKEN_FILE):
    tokens = load_tokens(filename)
    entry = tokens.get(email)
    if not entry:
        return None
    return entry["token"]

def validate_token(email, token, filename=TOKEN_FILE):
    tokens = load_tokens(filename)
    entry = tokens.get(email)
    if not entry:
        return False
    if entry["token"] == token and entry["count"] < RESEARCH_RUN_COUNT_TOKEN:
        entry["count"] += 1
        save_tokens(tokens, filename)
        return True
    return False

if __name__ == "__main__":
    email = input("Enter email: ").strip()
    token = generate_token()
    save_token(email, token)
    print(f"Token for {email}: {token}") 