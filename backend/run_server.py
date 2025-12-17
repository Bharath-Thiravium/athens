import os
import sys
import uvicorn

# Add the project directory to the Python path if needed
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Initialize Django
import django
django.setup()

# Print some debug information

if __name__ == "__main__":
    # Run Uvicorn
    uvicorn.run(
        "backend.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend", "authentication", "chatbox"],
        log_level="debug"
    )
