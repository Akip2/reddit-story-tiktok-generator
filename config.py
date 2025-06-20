
import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
PASSWORD = os.getenv('PASSWORD')
API_KEY = os.getenv("API_KEY")

assert CLIENT_ID, "CLIENT_ID missing"
assert CLIENT_SECRET, "CLIENT_SECRET missing"
assert REDDIT_USERNAME, "REDDIT_USERNAME missing"
assert PASSWORD, "PASSWORD missing"
assert API_KEY, "API_KEY missing"