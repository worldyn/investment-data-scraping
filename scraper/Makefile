########
# SETUP
# Assumes you already have:
# * Google Cloud SDK (gcloud CLI),
# * docker
########
# GCP-specific (Dataflow, GCR)
#gcloud config set project $GCP_PROJECT
#gcloud auth login
#gcloud auth configure-docker

setup:
	## Python environment
	pyenv virtualenv 3.9.12 beam-python
	pyenv activate beam-python

build:
	docker build --no-cache -t ${IMAGE} .
	docker push ${IMAGE}

	## You can launch a container using your image to make sure the contents are as expected:
	#docker run -it --entrypoint="/bin/bash" ${IMAGE}


######
# Running Pipelines
######
# Testing locally - NOTE: Local paths for input/output refer to the
# *container filesystem*, not your local filesystem; these will
# disappear when container finishes running.

run-local:
	python run_beam.py \
	--org=data_in/interview-test-org.json \
	--funding=data_in/interview-test-funding.json \
	--output=gs://${GCS_BUCKET}/enriched_final_beam.json \
	--runner=PortableRunner \
	--job_endpoint=embed \
	--environment_type="DOCKER" \
	--environment_config=${IMAGE} \

run-dataflow:
	python run_beam.py \
	--org=data_in/interview-test-org.json \
	--funding=data_in/interview-test-funding.json \
	--output=gs://${GCS_BUCKET}/enriched_final_beam.json \
	--runner=DataflowRunner \
	--job_endpoint=embed \
	--environment_type="DOCKER" \
	--environment_config=${IMAGE} \
	--temp_location "gs://${GCS_BUCKET}/tmp/" \
	--project $(GCP_PROJECT) \
	--region ${GCP_REGION} \
	--max_num_workers=2 \
    --num_workers=2 \
    --disk_size_gb=30 \
	--job_name=scraper

# Example - Dataflow
#python demo_pipeline.py \
#  --job_name "beam-customcontainer-demo" \
#  --input gs://dataflow-samples/shakespeare/kinglear.txt \
#  --output "gs://${GCS_BUCKET}/counts" \
#  --temp_location "gs://${GCS_BUCKET}/tmp/" \
#  --runner DataflowRunner \
#  --project $(gcloud config get-value project) \
#  --region $GCP_REGION\
  # CUSTOM CONTAINER FLAGS:
#  --experiment=use_runner_v2 \
#  --worker_harness_container_image=$IMAGE_URL
