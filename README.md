![Python](https://img.shields.io/badge/python-3.9+-blue) <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

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

Download Selenium chromedriver version [105.0.5195.19](https://chromedriver.storage.googleapis.com/index.html?path=105.0.5195.19/). I tried setting window size (258,258) in scraper/settings.py which gives me the mobile version width for the EQT website.

Put the driver in /scraper.

```bash
# Install packages
poetry install
```

```bash
# Authorize google cloud for uploading final data to Google Storage
gcloud auth login
gcloud config set project PROJECT_ID
```

```bash
# Set root dir env variable
export ROOT_DIR=./scraper
```

Assumes: 
- python is available with 'python' command
- interview-test-org.json and interview-test-funding.json put in scraper/data_in

### Schemas
See [Data Models](#DataModels)

My latest data version available in [here](https://storage.googleapis.com/eqt-interview/enriched_final_17-11-2022.json) (The resulting enriched data of the code)

### Pipeline Steps
Assumes that organisation and funding json files are in scraper/data_in (Add link?)

- scrape_portfolio.py: Scraping portfolio columns from https://eqtgroup.com/current-portfolio, producing json schema (A) 
- scrape_company.py: Scrape individual company data from https://eqtgroup.com/current-portfolio/company, producing schema (B)
- enrich_company.py: Enrich portfolio data with data from organisation+funding data, , producing schema (C)
- upload.py: Upload data to Google Storage
- run.py: Run whole pipeline. Assumes all file paths/names are based in ROOT_DIR environment variable

### Commands

```bash
# Run whole pipeline
poetry run python scraper/run.py -b bucket
```

```bash
# Run whole pipeline with a specific date (assumes day is enough granularity)
poetry run python scraper/run.py -b bucket -d dd-mm-yyyy
```

```bash
# Skip scraping step (assumes scraping is already done for same date)
poetry run python scraper/run.py -b bucket --noscrape
```

### Testing
```bash
python scraper/test.py
```

### DataModels
- (A) Portfolios: 
```
{
    "name": Str,
    "sector": Str,
    "country": Str,
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
    "country": Str,
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
    "country": Str,
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
### Future Improvements
- Improve portability by packaging python+selenium in docker
- Add script version to data filenames so that user knows which version produced the data
- Since each pipeline step is an executable ython file, it can easily be added to more complex pipelines, such as Airflow. With this you could do e.g scheduling, and produce some nice DAGs :)
- Use JSON schemas for validation
- Improve company name matching in parse_company_page() in scrape_company.py
- Scrape directly from data source