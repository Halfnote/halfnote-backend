
from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables only if running in development
if os.getenv("FLASK_ENV") == "development":
    load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)