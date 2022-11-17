""" 

"""
import subprocess
import argparse
from datetime import datetime
import os


def main():
    root_dir = os.environ["ROOT_DIR"]

    parser = argparse.ArgumentParser(description="Upload enriched data to GS")
    parser.add_argument(
        "-o", "--outdir", type=str, help="output directory", default="data_out"
    )
    parser.add_argument(
        "-n",
        "--outname",
        type=str,
        help="name of output json file (do not include json file ending)",
        default="enriched_final",
    )
    parser.add_argument(
        "-g",
        "--organisation",
        type=str,
        help="json file with organisational data",
        default="data_in/interview-test-org.json",
    )
    parser.add_argument(
        "-f",
        "--funding",
        type=str,
        help="json file with funding data",
        default="data_in/interview-test-funding.json",
    )
    parser.add_argument(
        "-b", "--bucket", required=False, type=str, help="Google storage bucket name"
    )
    parser.add_argument(
        "-d", "--date", required=False, type=str, help="Date in dd-mm-yyyy format"
    )
    parser.add_argument(
        "-s",
        "--noscrape",
        required=False,
        action=argparse.BooleanOptionalAction,
        help="Boolean: do not run scraping of portfolio and company data. Assumes you have run scraping before",
    )
    parser.add_argument(
        "-u",
        "--upload",
        required=False,
        action=argparse.BooleanOptionalAction,
        help="Boolean: only upload to GS. Assumes all other steps have been run",
    )
    args = parser.parse_args()

    if args.date:
        date = datetime.strptime(args.date, "%d-%m-%Y")
    else:
        now = datetime.now()
        date = now.strftime("%d-%m-%Y")

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # python_path = os.env.

    if not args.noscrape and not args.upload:
        print(f">>> Running portfolio scraper...")
        scrape_portfolio = subprocess.run(
            [
                "python",
                f"{root_dir}/scrape_portfolio.py",
                "-f",
                f"{root_dir}/{args.outdir}/portfolio_{date}.json",
            ]
        )
        print(f">>> Portfolio scraper return code: {scrape_portfolio.returncode}")

        print(f">>> Running individual company scraper...")
        scrape_company = subprocess.run(
            [
                "python",
                f"{root_dir}/scrape_company.py",
                "-i",
                f"{root_dir}/{args.outdir}/portfolio_{date}.json",
                "-o",
                f"{root_dir}/{args.outdir}/portfolio_enriched_{date}.json",
            ]
        )
        print(f"> Company scraper return code: {scrape_company.returncode}")

    if not args.upload:
        print(f">>> Enriching portfolio data...")
        enrich_company = subprocess.run(
            [
                "python",
                f"{root_dir}/enrich_company.py",
                "-i",
                f"{root_dir}/{args.outdir}/portfolio_enriched_{date}.json",
                "-o",
                f"{root_dir}/{args.outdir}/{args.outname}_{date}.json",
                "-g",
                f"{root_dir}/{args.organisation}",
                "-f",
                f"{root_dir}/{args.funding}",
            ]
        )
        print(f">>> Data enrichment return code: {enrich_company.returncode}")

    if args.bucket:
        print(
            f">>> Uploading data to GS location gs://{args.bucket}/{args.outname}_{date}.json ..."
        )
        upload = subprocess.run(
            [
                "python",
                f"{root_dir}/upload.py",
                "-i",
                f"{root_dir}/{args.outdir}/{args.outname}_{date}.json",
                "-b",
                f"{args.bucket}",
                "-d",
                f"{args.outname}_{date}.json",
            ]
        )
        print(f">>> Upload return code: {upload.returncode}")


if __name__ == "__main__":
    main()
