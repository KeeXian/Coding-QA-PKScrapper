from app.main import app
from flask_ngrok import run_with_ngrok

# Run the app in local tunnel
run_with_ngrok(app)
if __name__ == "__main__":
        app.run()