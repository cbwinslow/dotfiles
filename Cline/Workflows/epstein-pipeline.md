# Epstein Pipeline Workflow

## Document Scraping
```bash
# DOJ document downloads
cd ~/workspace/epstein
python scripts/download_doj.py --datasets <count>

# CDN downloads
python scripts/download_cdn.py --datasets <count>

# Monitor with dashboard
python scripts/dashboard.py
```

## Data Processing
```bash
# Run the processing pipeline
cd ~/workspace/epstein/Epstein-Pipeline
python -m pipeline.main

# Or use the epstein-ripper
cd ~/workspace/epstein/epstein-ripper
python ripper.py
```

## Database Queries
```bash
# Connect to PostgreSQL
psql -U cbwinslow -d epstein

# Common queries
\dt                          -- list tables
\d+ <table>                 -- describe table
SELECT count(*) FROM <table>; -- row count
```

## Common Tasks
- Adding new data sources: add to `scripts/`, update `TASKS.md`
- Pipeline changes: update `Epstein-Pipeline/`, run tests
- Analysis: use Jupyter or scripts in `scripts/` directory
