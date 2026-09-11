# NETSPORTS Backend

FastAPI + Jinja2 + Feather/Parquet storage esports tournament platform.

## Run

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python run.py
```

Open `http://localhost:8000`.

## First admin

Open `/admin/setup` once and create the admin account.

## PM2

```bash
pm2 start run.py --interpreter python3 --name netsports
pm2 save
```

## Important production settings

Set a real `SECRET_KEY` in `app/config.py` or move it to an environment variable before deployment.

Optional SMTP:
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SMTP_FROM

## Data

All persistent data is stored in `data/*.feather`.
Uploads are stored in `static/uploads/`.

The current implementation intentionally keeps the storage layer isolated in `app/database.py` so it can later be migrated to SQLite/PostgreSQL without rewriting the routes.
