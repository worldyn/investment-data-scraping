""" 
Enrich company data with organisational and funding data
"""
import json
from tqdm import tqdm
import argparse
import re
import uuid


def prep_company_name(company_name):
    """ 
    Put company name string into a comparable format for other data sources.
    Does lower casing, filtering out common words, removing spaces, etc
    
    Parameters:
    company_name (Str): the original company string

    Returns:
    Str: cleaned company string
    """
    company_name = company_name.lower().strip()
    company_name = company_name.replace("-", " ")  # e.g AM-Pharma to AM Pharma
    if (
        "/" in company_name
    ):  # remove second company, e.g kuoni group / vfs global to kuoni group
        i = company_name.index("/")
        company_name = company_name[:i]

    common_words = [
        "ltd",
        "ltd.",
        "inc",
        "inc.",
        "limited",
        "corp",
        "corp.",
        "llc",
        "llc.",
    ]
    for w in common_words:
        company_name.replace(w, "")

    company_name = re.sub(r" +", " ", company_name)
    return company_name


def prep_url(url):
    """ 
    Remove protocol from url and additional unecessary '/'
    
    Parameters:
    url (Str): original url

    Returns:
    Str: cleaned url
    """
    domain = url.replace("https://", "").replace("http://", "")
    if domain[-1] == "/":
        domain = domain[:-1]
    return domain


def main():
    parser = argparse.ArgumentParser(
        description="Enrich individual companies with organisational and \
         funding data. You must set input and output json file names"
    )
    parser.add_argument(
        "-i", "--input", required=True, type=str, help="input json file"
    )
    parser.add_argument(
        "-g",
        "--organisation",
        required=True,
        type=str,
        help="json file with organisational data",
    )
    parser.add_argument(
        "-f", "--funding", required=True, type=str, help="json file with funding data"
    )
    parser.add_argument("-o", "--out", required=True, type=str, help="out json file")
    args = parser.parse_args()

    # Load files
    with open(args.input, "r") as f:
        portfolio = json.load(f)["portfolio"]
    orgs = []
    funding = []
    with open(args.organisation, "r") as f:
        for line in f:
            orgs.append(json.loads(line))
        print(orgs[0].keys())
    with open(args.funding, "r") as f:
        for line in f:
            funding.append(json.loads(line))
        print(funding[0].keys())

    # Count number of misses for portfolio companies
    org_misses = 0
    funding_misses = 0

    portfolio_enriched = []
    for company in tqdm(portfolio):
        # prepare company info to comparable formats
        company_name = prep_company_name(company["name"])

        if "web" in company.keys():
            domain = prep_url(company["web"])
        else:
            domain = None
        company["uuid"] = None
        # print(f"domain: {domain}")

        # Add organistional info
        for org in orgs:
            domain_org = org.get("homepage_url")
            if domain_org:
                domain_org = prep_url(domain_org)
            name_org = org["company_name"].lower().strip()
            # name_org = re.sub(r'[^\w\s]', '', name_org)
            if (
                "web" in company.keys() and domain == domain_org
            ) or company_name in name_org:
                company["uuid"] = org.get("uuid")
                company["country_code"] = org.get("country_code")
                company["city"] = org.get("city")
                company["founded_on"] = org.get("founded_on")
                company["short_description"] = org.get("short_description")
                company["description"] = org.get("description")
                company["funding_rounds"] = org.get("funding_rounds")
                company["funding_total_usd"] = org.get("funding_total_usd")
                company["employee_count"] = org.get("employee_count")

        if company["uuid"] == None:
            # print(f'No match org data: {company_name}')
            company["uuid"] = str(uuid.uuid1())
            org_misses += 1
        else:
            # print(f'Match org data: {company_name}')
            pass

        # Add funding info
        company["fundings"] = []
        for fund in funding:
            # funding_round_uuid', 'company_uuid', 'company_name', 'investment_type', 'announced_on', 'raised_amount_usd', 'investor_names
            name_funding = fund["company_name"].lower().strip()

            if company_name in name_funding:
                company["fundings"].append(
                    {
                        "funding_round_uuid": fund.get("funding_round_uuid"),
                        "investment_type": fund.get("investment_type"),
                        "announced_on": fund.get("announced_on"),
                        "raised_amount_usd": fund.get("raised_amount_usd"),
                        "investor_names": fund.get("investor_names"),
                    }
                )

        if len(company["fundings"]) == 0:
            # print(f'No match funding data: {company_name}')
            funding_misses += 1
        else:
            # print(f'Match funding data: {company_name}')
            pass

        portfolio_enriched.append(company)

    print(f"> Miss rate for organisational data: {float(org_misses)/len(portfolio)}")
    print(f"> Miss rate for funding data: {float(funding_misses)/len(portfolio)}")

    print(f"> Saving to json file")
    json_obj = json.dumps({"portfolio": portfolio_enriched}, indent=4)
    with open(args.out, "w") as o:
        o.write(json_obj)


if __name__ == "__main__":
    main()
