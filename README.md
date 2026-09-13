# Ardhiya (أرضية)

A bilingual (Arabic/English) real estate landing page built with FastAPI, SQLAlchemy 2.x, Alembic, and Jinja2 templates with Tailwind CSS and Alpine.js via CDN.

## Features

- Bilingual support (ar/en) with RTL/LTR handling
- Two search methods: specs form and image upload
- Buyer request tracking with session IDs
- Responsive down to 320px
- No build step — all CSS/JS via CDN

## Tech Stack

- Python 3.11+, FastAPI, Uvicorn
- SQLAlchemy 2.x (DeclarativeBase, Mapped, mapped_column)
- Alembic for migrations
- Jinja2 templates with reusable macros
- Tailwind CSS + Alpine.js (CDN)
- SQLite (default, configurable via DATABASE_URL)

## Project Structure

```
ardhiya/
├── app/
│   ├── core/          # config, database, storage, i18n
│   ├── modules/       # landing, buyer_requests, media, properties
│   ├── templates/     # Jinja2 templates with macros
│   └── static/        # CSS, JS, uploads
├── alembic/           # migrations
└── requirements.txt
```

# file: README.md
# Ardhiya-Real-Estate-Landing-Page
# Ardhiya-Real-Estate-Landing-Page
# Ardhiya-Real-Estate-Landing-Page
