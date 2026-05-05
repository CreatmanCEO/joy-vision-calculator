# Changelog

Все значимые изменения в проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

---

## [Unreleased]

### Added
- `LICENSE` (proprietary / all-rights-reserved, portfolio-only publication)
- `README.ru.md` — Russian mirror of the README
- `docs/architecture.svg` — Bitrix24 integration + Flask module diagram
- `docs/screenshots/` (calculator + orders) and `docs/demos/orders-flow.mp4`
- `.github/workflows/validate.yml` — meta-file presence, JSON validity, Markdown link check

### Changed
- README rewritten: badges, screenshots gallery, demo-video link, "Why this exists / How it works", tech-stack table, Limitations section, ecosystem links, expanded author block

### Планируется
- Расчёт комплектующих (Slider L/X, JV Line, Zig-Zag)
- CRUD заказов
- Генерация PDF (КП, разблюдовка)
- Управление ценами
- Интеграция с Битрикс24

---

## [0.1.0] - 2026-02-20

### Добавлено
- Инициализация проекта
- Структура каталогов
- Документация:
  - AS-IS / TO-BE анализ
  - Модель данных
  - API спецификация
  - Дизайн-документ
- README.md
- requirements.txt

### Источники кода
- `calculator.py` — расчёт комплектующих (будет интегрирован)
- `reader_0.2.py` — генерация PDF разблюдовки (будет адаптирован)
- `old/core/bitrix_api.py` — интеграция с Битрикс (будет перенесён)

---

## Версионирование

- **MAJOR** — несовместимые изменения API
- **MINOR** — новая функциональность с обратной совместимостью
- **PATCH** — исправления багов
