# Epstein Project Rules

## Project Structure
- Root: `~/workspace/epstein/`
- Python 3.12+ project with pyproject.toml
- Key directories: `scripts/`, `data/`, `EpsteinLibraryMediaScraper/`, `Epstein-Pipeline/`, `epstein-ripper/`
- Databases: PostgreSQL (`epstein` DB on localhost:5432), SQLite files in project root

## Conventions
- Use `uv` or `uvx` for Python package management
- Playwright for browser automation (scraping)
- spaCy + GLiNER for NLP entity extraction
- OpenCV/Insightface for image analysis
- Pandas/PyArrow for data processing
- aiohttp for async HTTP

## Coding Standards
- Python: follow PEP 8, use type hints
- Prefer async patterns (aiohttp, asyncio) for I/O-bound operations
- Use context managers for database connections
- Log to stderr or structured log files, not print()
- Keep .env files for secrets (never commit them)

## Data Pipeline Flow
1. Scrape → download documents/media (Playwright, aiohttp)
2. Parse → extract text from PDFs/images (PyMuPDF, OCR)
3. Process → NLP entity extraction, classification
4. Store → PostgreSQL / SQLite databases
5. Analyze → queries, dashboards, reports

## Security
- Never expose API keys or database credentials in code
- Use environment variables from .env files
- The .gitignore already excludes *.db, *.pdf, .env
