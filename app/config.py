from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
SECRET_KEY = "CHANGE_THIS_IN_PRODUCTION_TO_A_LONG_RANDOM_SECRET"
SITE_NAME = "NETSPORTS"
