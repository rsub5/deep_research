import secrets
import json
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables from .env for local development
load_dotenv()

# Fail-fast: Ensure all required environment variables are set
TOKEN_FILE = os.getenv("TOKEN_FILE")
if not TOKEN_FILE:
    raise ValueError("TOKEN_FILE environment variable is not set. Please set it in your environment.")

FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise ValueError('FERNET_KEY environment variable is not set. Please set it in your environment.')
fernet = Fernet(FERNET_KEY.encode())

RESEARCH_RUN_COUNT_TOKEN = 2

def generate_token(length=16):
    """Generate a secure random token."""
    return secrets.token_hex(length)

def save_token(email, token, filename=TOKEN_FILE):
    tokens = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            tokens = json.load(f)
    encrypted_token = fernet.encrypt(token.encode()).decode()
    tokens[email] = {"token": encrypted_token, "count": 0}
    with open(filename, "w") as f:
        json.dump(tokens, f)

def get_token(email, filename=TOKEN_FILE):
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        tokens = json.load(f)
    entry = tokens.get(email)
    if not entry:
        return None
    try:
        return fernet.decrypt(entry["token"].encode()).decode()
    except Exception:
        return None

def validate_token(email, token, filename=TOKEN_FILE):
    if not os.path.exists(filename):
        return False
    with open(filename, "r") as f:
        tokens = json.load(f)
    entry = tokens.get(email)
    if not entry:
        return False
    try:
        real_token = fernet.decrypt(entry["token"].encode()).decode()
        if real_token == token and entry["count"] < RESEARCH_RUN_COUNT_TOKEN:
            entry["count"] += 1
            with open(filename, "w") as f:
                json.dump(tokens, f)
            return True
        return False
    except Exception:
        return False

if __name__ == "__main__":
    email = input("Enter email: ").strip()
    token = generate_token()
    save_token(email, token)
    print(f"Token for {email}: {token}") 