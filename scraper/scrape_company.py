""" 
Enrich portfolio company data from individual company pages on EQT website.
"""
from bs4 import BeautifulSoup
from tqdm import tqdm
from settings import setup_driver
import re
import apache_beam as beam
import logging


def parse_company_page(page_source, company):
    """ 
    Extract additional data about specific company from an EQT page
    "https://eqtgroup.com/current-portfolio/" + company name,
    e.g https://eqtgroup.com/current-portfolio/hmi-group
    
    Parameters:
    page_source (Str): html page
    company (dict): dictionary consisiting of company data

    Returns:
    dict: enriched dictionary for company data
    """
    soup = BeautifulSoup(page_source, "lxml")
    divs = soup.find_all("div", class_="text-secondary-darker")

    if len(divs) == 0:
        # no extra data available
        return company

    # first div contains company info and website:
    if divs[0].find("ul"):
        for li in divs[0].find("ul").find_all("li", class_="flex", recursive=False):
            m = li.find_all("div", recursive=False)

            col_name = m[0].find("span").get_text().lower()
            if col_name != "fund":
                if m[1].find("a"):
                    value = m[1].find("a")["href"]
                else:
                    value = m[1].find("span").get_text()
                company[col_name] = value

    # look for management and board:
    def add_members(ul):
        # Re-using parsing format for similar DOM below
        member_list = []
        for li in ul.find_all("li", recursive=False):
            m = li.find_all("div", recursive=False)
            role = m[0].find("span").get_text()
            name = m[1].find("span").get_text()
            member_list.append({"role": role, "name": name})
        return member_list

    for d in divs[1:]:
        if d.find("h3", recursive=False):
            if "board of directors" in d.find("h3", recursive=False).get_text().lower():
                board = add_members(d.find("ul"))
                company["board"] = board
            if "management" in d.find("h3", recursive=False).get_text().lower():
                management = add_members(d.find("ul"))
                company["management"] = management

    return company

class Companies(beam.DoFn):
    def __init__(self):
        pass

    def process(self, company):
        # get company name in correct url format
        try:
            self.driver = setup_driver()
        except Exception as e:
            print(f'> EXCEPTION selenium driver: {str(e)}')

        company_name = company["name"]
        company_name = re.sub(r"&", "-", company_name)
        company_href = re.sub(r"[^&A-Za-z0-9]+", " ", company_name.lower()).strip()
        company_href = re.sub(r" +", "-", company_href)
        url = "https://eqtgroup.com/current-portfolio/" + company_href

        self.driver.get(url)
        page_source = self.driver.page_source

        print(f"URL {url}")
        #logging.info(f"URL {url}")
        if not "<div>" in page_source:
            logging.info(f"> Could NOT do fetch: {url}")
            yield company

        yield parse_company_page(page_source, company)