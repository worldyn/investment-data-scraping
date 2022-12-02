""" 

"""
import subprocess
import argparse
from datetime import datetime
import os
from scrape_portfolio import Portfolio
from scrape_company import Companies
from enrich_company import EnrichPortfolio
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions,SetupOptions
from settings import setup_driver
import logging
import json
from apache_beam.io import WriteToText


def parse_jsonl(file):
    data = []
    with open(file) as f:
        data.extend(json.loads(line) for line in f)
    return data

def run(argv=None, save_main_session=True):  # sourcery skip: extract-method
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--org',
        default='gs://motherbrain-external-test/interview-test-org.json.gz',
        help='Organisation data source and filename'
    )
    parser.add_argument(
        '--funding',
        default='gs://motherbrain-external-test/interview-test-funding.json.gz',
        help='Organisation data source and filename'
    )
    parser.add_argument(
        '--output',
        default='gs://eqt-interview/enriched_final_beam.json',
        help='Organisation data source and filename'
    )
    
    args, pipeline_args = parser.parse_known_args(argv)
    logging.info(f"Pipeline args: {pipeline_args}")
    pipeline_options = PipelineOptions(pipeline_args)
    
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    #driver = setup_driver()

    with beam.Pipeline(options=pipeline_options) as p:
        logging.info("Getting portfolio...")
        portfolio = (p  | beam.Create(["https://eqtgroup.com/current-portfolio"])
                        | 'Get Portfolio' >> beam.ParDo(Portfolio(limit=True))
                        | 'Get Company info' >> beam.ParDo(Companies()))
        
        organisations = parse_jsonl(args.org)
        funding = parse_jsonl(args.funding)

        print("Writing enriched portfolio...")
        logging.info("Writing enriched portfolio...")
        portfolio_enriched = (
            portfolio   | 'Enrich Portfolio' >> beam.ParDo(EnrichPortfolio(organisations,funding))
                        | 'FormatOutput' >> beam.Map(json.dumps)
                        | 'Write' >> WriteToText(args.output)
        )

    #driver.quit()

    #with beam.Pipeline(options=pipeline_options) as p:
    #    (p 
    #    | 'Read files' >> ReadFromTextWithFilename(known_args.input))

if __name__ == '__main__':
    '''
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.job_name = 'setJobName'
    google_cloud_options.project = 'projectName'
    google_cloud_options.staging_location = 'stagingBucketLocation'
    google_cloud_options.temp_location = 'tempBucketLocation'
    options.view_as(StandardOptions).runner = 'DataflowRunner'
    '''
    logging.getLogger().setLevel(logging.INFO)
    run()