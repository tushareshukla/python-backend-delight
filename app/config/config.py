import os
from dotenv import load_dotenv

load_dotenv()

COLLY_MICROSERVICE_BASE_URL = os.getenv("COLLY_MICROSERVICE_BASE_URL", "http://localhost:8000")
