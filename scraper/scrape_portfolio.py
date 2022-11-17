""" 
Scrape data from the EQT portfolio site and save into json file
"""

import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import argparse
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


def main():
    parser = argparse.ArgumentParser(
        description="Get portfolio companies data, set output file name"
    )
    parser.add_argument(
        "-f", "--file", required=True, type=str, help="output json file"
    )
    args = parser.parse_args()

    driver = setup_driver()
    url = "https://eqtgroup.com/current-portfolio"
    driver.get(url)
    page_source = driver.page_source

    with open("page.html", "w") as file:
        file.write(page_source)

    return
    assert "<div>" in page_source

    # extract row-wise elements
    soup = BeautifulSoup(page_source, "lxml")
    rows_json = []
    rows = (
        soup.find("div", class_="order-last")
        .find("ul")
        .find_all("li", class_="flex", recursive=False)
    )
    print(f"> Number of data point rows: {len(rows)}")

    assert len(rows) > 0

    for r in tqdm(rows):
        data_row = parse_row(r)
        rows_json.append(data_row)

    print("> Saving to file")

    json_obj = json.dumps({"portfolio": rows_json}, indent=4)
    with open(args.file, "w") as o:
        o.write(json_obj)
    driver.quit()


if __name__ == "__main__":
    main()
