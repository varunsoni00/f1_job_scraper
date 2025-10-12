# F1 Job Scraper – Automated Formula 1 Careers Aggregator

This project scrapes job listings from official Formula 1 team career portals and compiles them into a single Excel file — one sheet per team (TeamName-JobCount).

## Features

- Scrapes multiple F1 team career portals (each team has a custom scraper)
- Outputs a multi-sheet Excel: `output/F1_Jobs.xlsx`
- Minimal setup and easy to run

## Quick start

```bash
# create and activate virtual environment (if not already)
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the scraper
python src/main.py
```

## Output

The Excel file will be created at: `output/F1_Jobs.xlsx`

## Project Structure

```
f1-job-scraper/
├─ src/
│  ├─ main.py
│  └─ scrapper.py
├─ data/
├─ docs/
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md

```

## License

MIT (see LICENSE file)

## Project Last Updated

13th October 2025
