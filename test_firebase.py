# test_firebase.py
import os
# Optional: load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed – continue without .env
import firebase_admin
from firebase_admin import credentials, firestore
import pathlib

_priv_key = os.getenv("FIREBASE_PRIVATE_KEY")
if _priv_key:
    _priv_key = _priv_key.replace("\\n", "\n")

# Initialise using the service‑account JSON file (recommended)
BASE_DIR = pathlib.Path(__file__).parent
cred_path = BASE_DIR / "serviceAccountKey.json"
# Verify the file exists – give a clear message if it does not
if not cred_path.is_file():
    raise FileNotFoundError(f"Service account file not found at {cred_path}.\nDownload it from Firebase Console → Project Settings → Service accounts → Generate new private key and place it here.")
admin_cred = credentials.Certificate(str(cred_path))
firebase_admin.initialize_app(admin_cred)
db = firestore.client()

if __name__ == "__main__":
    # Simple sanity check – list collections and test write/read
    print("Collections:", [c.id for c in db.collections()])
    test_ref = db.collection("firestore_test").document("cli_demo")
    test_ref.set({"ping": "pong"})
    ok = test_ref.get().to_dict()["ping"] == "pong"
    print("Write‑read OK:", ok)
    test_ref.delete()
test_ref.set({"ping": "pong"})
print("Write‑read OK:", test_ref.get().to_dict()["ping"] == "pong")
test_ref.delete()
