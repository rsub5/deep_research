from dotenv import load_dotenv
import os
import json
from cryptography.fernet import Fernet

# Load environment variables from .env
load_dotenv()

TOKEN_FILE = "tokens.json"
FERNET_KEY = os.getenv('FERNET_KEY')
print(f"FERNET_KEY initialized")
if not FERNET_KEY:
    raise ValueError('FERNET_KEY not set in environment')
fernet = Fernet(FERNET_KEY.encode())

def decrypt_tokens(filename=TOKEN_FILE):
    if not os.path.exists(filename):
        print(f"Token file '{filename}' does not exist.")
        return
    with open(filename, "rb") as f:
        encrypted = f.read()
    if not encrypted:
        print(f"[ERROR] Token file '{filename}' is empty. Please generate a token first.")
        return
    try:
        decrypted = fernet.decrypt(encrypted)
        tokens = json.loads(decrypted.decode())
    except Exception as e:
        print(f"[ERROR] Could not decrypt file: {e}")
        return
    print("Decrypted tokens:")
    for email, entry in tokens.items():
        try:
            token = entry["token"]
            count = entry.get("count", 0)
            print(f"{email}: {token} (used {count} times)")
        except Exception as e:
            print(f"[ERROR] Could not read token for {email}: {e}")

if __name__ == "__main__":
    decrypt_tokens() 