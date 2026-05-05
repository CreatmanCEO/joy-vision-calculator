# Joy Vision Calculator

[![License: Proprietary](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/CreatmanCEO/joy-vision-calculator?style=social)](https://github.com/CreatmanCEO/joy-vision-calculator/stargazers)
[![Validate](https://github.com/CreatmanCEO/joy-vision-calculator/actions/workflows/validate.yml/badge.svg)](https://github.com/CreatmanCEO/joy-vision-calculator/actions/workflows/validate.yml)
[![Status: delivered](https://img.shields.io/badge/status-delivered-blue)]()
[![Platform: Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com/)

Web app for calculating frameless glazing component lists, generating commercial-offer / specification PDFs, and pushing orders into Bitrix24 CRM. Built for [Joy Vision](https://joyvision.ru) — a Russian frameless-glazing manufacturer — to replace a manual Excel-based workflow.

> Russian version: [README.ru.md](README.ru.md)

## Screenshots

| Calculator | Orders list |
|---|---|
| ![Calculator](docs/screenshots/01-calculator.jpg) | ![Orders list](docs/screenshots/02-orders.jpg) |

[Demo video — orders flow](docs/demos/orders-flow.mp4) (~1.9 MB, GitHub renders inline).

## Why this exists

Joy Vision's pre-software process: a sales engineer measured the opening, opened a master Excel sheet, copied formulas, manually built a parts list, exported a PDF, then re-typed the deal into Bitrix24. Two windows of the same opening could take 30–40 minutes and frequently produced wrong specs.

This app collapses that into a single form:

1. Pick system type, enter dimensions and quantity.
2. Calculator emits a parts list against the live price list.
3. One click → commercial-offer PDF + parts spec PDF.
4. One click → order pushed to Bitrix24 as a deal with documents attached.

## How it works

```
Browser (Bootstrap form)
      │  POST /api/orders
      ▼
Flask app (app.py)
      │
      ├─ modules/calculator/  → parts list per system type
      ├─ modules/pricing/     → reads SQLite price catalog
      ├─ modules/pdf/         → ReportLab → KP + spec PDFs
      └─ modules/bitrix/      → REST webhook → Bitrix24 deal
```

Supported systems:

- **Slider L** — parallel-sliding
- **Slider X** — reinforced parallel-sliding
- **JV Line** — with parking
- **JV Zig-Zag** — accordion

Architecture diagram: [`docs/architecture.svg`](docs/architecture.svg).

## Tech stack

| Layer        | Tool                              |
|--------------|-----------------------------------|
| Language     | Python 3.10+                      |
| Web          | Flask 3.x                         |
| ORM          | SQLAlchemy 2.x + Flask-SQLAlchemy |
| Migrations   | Flask-Migrate (Alembic)           |
| Database     | SQLite (default), PostgreSQL ready |
| PDF          | ReportLab 4.x                     |
| Excel I/O    | pandas 2.x + openpyxl 3.x         |
| HTTP client  | requests 2.31+                    |
| WSGI         | Gunicorn 21+                      |
| Tests        | pytest + pytest-flask             |
| Frontend     | Server-rendered Jinja2 + Bootstrap |
| CRM          | Bitrix24 incoming webhook         |

## Quick start

### Requirements

- Windows 10/11 or Ubuntu 20.04+
- Python 3.10+
- ~500 MB free disk

### Install

**Windows:**
```bat
git clone https://github.com/CreatmanCEO/joy-vision-calculator.git
cd joy-vision-calculator
install.bat
```

**Ubuntu (VPS):**
```bash
git clone https://github.com/CreatmanCEO/joy-vision-calculator.git
cd joy-vision-calculator
chmod +x install.sh
sudo ./install.sh
```

Detailed walkthroughs:

- [Windows install](INSTALL_WINDOWS.md)
- [Ubuntu / VPS install](INSTALL_UBUNTU.md)
- [Bitrix24 setup](docs/BITRIX_SETUP.md)
- [Tilda integration](TILDA_INTEGRATION.md)

## Configuration

Settings live in `.env` (copy from `.env.example`):

```env
SECRET_KEY=                  # Flask secret — change before production
BITRIX24_WEBHOOK_URL=        # incoming webhook URL
BITRIX24_FOLDER_ID=          # Bitrix24 folder id for documents
DATABASE_URL=                # sqlite:///data/app.db (default) or postgresql://...
```

## API

After install, REST endpoints are exposed at `http://localhost:5000/api`:

| Method | Path                          | Purpose                       |
|--------|-------------------------------|-------------------------------|
| GET    | `/api/orders`                 | list orders                   |
| POST   | `/api/orders`                 | create order                  |
| GET    | `/api/orders/{id}`            | fetch order                   |
| PUT    | `/api/orders/{id}`            | update order                  |
| DELETE | `/api/orders/{id}`            | delete order                  |
| POST   | `/api/orders/{id}/systems`    | add system to order           |
| GET    | `/api/orders/{id}/pdf/kp`     | commercial-offer PDF          |
| GET    | `/api/orders/{id}/pdf/spec`   | parts spec PDF                |
| GET    | `/api/prices`                 | list price entries            |
| POST   | `/api/prices/import`          | import price list from Excel  |
| POST   | `/api/bitrix/sync/{id}`       | push order to Bitrix24        |

## Tests

```bash
pytest tests/ -v
```

## Limitations

- Single-tenant: no user accounts or per-company isolation.
- Calculation rules are tuned for Joy Vision's catalog; reusing for another manufacturer requires editing `modules/calculator/` and `models/price.py`.
- Bitrix24 integration uses incoming webhooks (no OAuth flow); webhook URL is a long-lived secret.
- PDF templates are Russian-only (KP / разблюдовка).
- No automated frontend tests; only backend pytest coverage.
- SQLite is the default DB; switch to PostgreSQL via `DATABASE_URL` if you expect concurrent writers.

## Project structure

```
joy-vision-calculator/
├── app.py                # Flask entry
├── config.py             # config loader
├── extensions.py         # SQLAlchemy / Migrate
├── models/               # ORM models (Order, System, Price, ...)
├── modules/
│   ├── calculator/       # parts-list logic per system
│   ├── orders/           # order REST API
│   ├── pricing/          # price-list REST API + Excel import
│   ├── pdf/              # ReportLab PDF generation
│   └── bitrix/           # Bitrix24 webhook client
├── templates/            # Jinja2 templates
├── static/               # CSS/JS/Bootstrap
├── tests/                # pytest suite
└── docs/                 # diagrams, screenshots, demo video
```

## Related — Claude Code ecosystem by the same author

Sister repos exploring Claude Code workflows, context engineering, and agent tooling:

- [`claude-code-antiregression-setup`](https://github.com/CreatmanCEO/claude-code-antiregression-setup)
- [`ai-context-hierarchy`](https://github.com/CreatmanCEO/ai-context-hierarchy)
- [`claude-statusline`](https://github.com/CreatmanCEO/claude-statusline)
- [`notebooklm-claude-workflows`](https://github.com/CreatmanCEO/notebooklm-claude-workflows)
- [`webtest-orch`](https://github.com/CreatmanCEO/webtest-orch)
- [`hydrowatch`](https://github.com/CreatmanCEO/hydrowatch)
- [`lingua-companion`](https://github.com/CreatmanCEO/lingua-companion)
- [`security-scanner`](https://github.com/CreatmanCEO/security-scanner)
- [`diabot`](https://github.com/CreatmanCEO/diabot)
- [`portfolio`](https://github.com/CreatmanCEO/portfolio)
- [`ghost-showcase`](https://github.com/CreatmanCEO/ghost-showcase)
- [`cc-janitor`](https://github.com/CreatmanCEO/cc-janitor) — active development

## Author

**Nick Podolyak** — full-stack engineer.

- GitHub: [@CreatmanCEO](https://github.com/CreatmanCEO)
- Habr: [creatman](https://habr.com/ru/users/creatman/)
- dev.to: [@creatman](https://dev.to/creatman)
- Telegram: [@Creatman_it](https://t.me/Creatman_it)
- Site: [creatman.site](https://creatman.site)

## License

Proprietary. Source published for portfolio purposes only — see [LICENSE](LICENSE). Commercial reuse requires written permission.
