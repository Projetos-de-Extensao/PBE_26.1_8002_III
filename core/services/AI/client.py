from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    api_key = "dummy_api_key_to_avoid_import_errors"

client = genai.Client(api_key=api_key)

