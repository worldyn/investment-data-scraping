![Python](https://img.shields.io/badge/python-3.9+-blue)

# EQT Portfolio Data Enrichment

A pipeline that enriches the information on EQT portfolio companies scraped from the public EQT website with the data from other datasets. The resulting enriched dataset is exported to Google Storage.

## Structure

``` text
├── pyproject.toml
├── poetry.lock
├── scraper
│   ├── __init__.py
│   ├── chromedriver
│   ├── enrich_company.py
│   ├── run.py
│   └── scrape_company.py
│   └── scrape_portfolio.py
│   └── settings.py
│   └── test.py
│   └── upload.py
```

### Install

Download a Selenium [chromedriver](https://chromedriver.chromium.org/downloads)
that matches your chrome version. Put the driver in /scraper

```bash
# Install packages
poetry install
```

```bash
# Authorize google cloud for uploading final data to Google Storage
gcloud auth login
gcloud config set project PROJECT_ID
```

### Schemas
See [Data Models](#DataModels)

### Pipeline Steps
Assumes that organisation and funding json files are in scraper/data_in (Add link?)

- scrape_portfolio.py: Scraping portfolio columns from https://eqtgroup.com/current-portfolio, producing json schema (A) 
- scrape_company.py: Scrape individual company data from https://eqtgroup.com/current-portfolio/company, producing schema (B)
- enrich_company.py: Enrich portfolio data with data from organisation+funding data, , producing schema (C)
- upload.py: Upload data to Google Storage
- run.py: Run whole pipeline

### Commands

```bash
# Run whole pipeline
python scraper/run.py -b bucket
```

### Testing
```bash
# Run whole pipeline
python scraper/test.py
```

### DataModels
- (A) Portfolios: 
```
{
    "name": Str,
    "sector": Str,
    "country": "China",
    "fund": [
                {
                    "name": Str,
                    "link": Str
                }
            ],
    "entry": Str
}
```

- (B) Portfolios2: 
```
{
    "name": Str,
    "sector": Str,
    "country": "China",
    "fund": [
                {
                    "name": Str,
                    "link": Str
                },
            ],
    "entry": Str
    "web": Str,
    "board": [
        {
            "role": Str,
            "name": Str
        },
    ],
    "management": [
        {
            "role": Str,
            "name": Str
        },
    ]
}
```

- (B) Portfolios Enriched: 
```
{
    "uuid": Str
    "name": Str,
    "sector": Str,
    "country": "China",
    "fund": [
                {
                    "name": Str,
                    "link": Str
                },
            ],
    "entry": Str
    "web": Str,
    "board": [
        {
            "role": Str,
            "name": Str
        },
    ],
    "management": [
        {
            "role": Str,
            "name": Str
        },
    ],
    "country_code": Str,
    "city": Str,
    "founded_on": Str,
    "short_description": Str
    "description": Str
    "funding_rounds": Str,
    "funding_total_usd": Str,
    "employee_count": Str,
    "fundings": [
        {
            "funding_round_uuid": Str,
            "investment_type": Str,
            "announced_on": Str,
            "raised_amount_usd": Str,
            "investor_names": Str
        },
    ]
}
```
