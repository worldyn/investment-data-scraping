""" 
Scrape data from the EQT portfolio site and save into json file
"""

from bs4 import BeautifulSoup
from tqdm import tqdm
import apache_beam as beam
import logging
from settings import setup_driver


def parse_row(r):
    """ 
    Extracts portfolio data column names and values per row
    
    Parameters:
    r (Str): <li> row DOM element

    Returns:
    dict: dictionary consisiting of portfolio company data columns
    """
    divs = r.find_all("div", recursive=False)

    assert len(divs) > 0

    name = divs[0].find("span", class_="inline-block").get_text()

    assert name is not None

    data_row = {"name": name}

    other_cols = divs[1].find("ul").find_all("li", recursive=False)
    for col in other_cols:
        col_content = col.find_all("span", recursive=False)
        col_name = col_content[0].get_text().lower()
        col_data = col_content[1]

        if col_data.find("ul"):  # multiple entries
            data_row[col_name] = []
            entries = col_data.find("ul").find_all("li", recursive=False)

            for e in entries:
                if e.find("a"):
                    a = e.find("a")
                    data_row[col_name].append({"name": a.get_text(), "link": a["href"]})
                else:
                    data_row[col_name].append({"name": e.get_text()})
        else:
            data_row[col_name] = col_content[1].get_text()
    return data_row


class Portfolio(beam.DoFn):
    def __init__(self, limit=False):
        #self.driver = driver
        #self.driver = setup_driver()
        self.limit = limit
        pass
    
    def process(self, url):
        logging.info(f"> Processing rows for {url}...")
        print(f"> Processing rows for {url}...")

        #assert self.driver is not None
        try:
            self.driver = setup_driver()
        except Exception as e:
            print(f'> EXCEPTION selenium driver: {str(e)}')

        self.driver.get(url)
        page_source = self.driver.page_source

        assert "<div>" in page_source

        # extract row-wise elements
        soup = BeautifulSoup(page_source, "lxml")
        rows = (
            soup.find("div", class_="order-last")
            .find("ul")
            .find_all("li", class_="flex", recursive=False)
        )
        logging.info(f"> Number of data point rows: {len(rows)}")

        assert len(rows) > 0

        i = 0
        for r in tqdm(rows):
            if self.limit and i > 3:
                break
            data_row = parse_row(r)
            yield data_row
            i += 1
        
       
        


