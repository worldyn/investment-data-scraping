""" 
Enrich portfolio company data from individual company pages on EQT website.
"""
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import argparse
from settings import setup_driver
import re


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

def main():
    parser = argparse.ArgumentParser(
        description="Get additional data from specific company. You must set input and output json file names"
    )
    parser.add_argument(
        "-i", "--input", required=True, type=str, help="input json file"
    )
    parser.add_argument("-o", "--out", required=True, type=str, help="out json file")
    args = parser.parse_args()

    driver = setup_driver()

    with open(args.input, "r") as f:
        portfolio = json.load(f)["portfolio"]

    assert len(portfolio) > 0

    portfolio_enriched = []
    for company in tqdm(portfolio):
        # get company name in correct url format
        company_name = company["name"]
        company_href = re.sub(r"[^\w\s]", " ", company_name.lower()).strip()
        company_href = re.sub(r" +", "-", company_href)
        url = "https://eqtgroup.com/current-portfolio/" + company_href

        driver.get(url)
        page_source = driver.page_source

        assert '<div>' in page_source

        portfolio_enriched.append(parse_company_page(page_source, company))

    print("> Saving to json file")
    json_obj = json.dumps({"portfolio": portfolio_enriched}, indent=4)
    with open(args.out, "w") as o:
        o.write(json_obj)
    driver.quit()


if __name__ == "__main__":
    main()
