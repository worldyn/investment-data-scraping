# This can be any container image,
FROM apache/beam_python3.9_sdk

# Install SDK. (needed for Python SDK)
RUN pip install --no-cache-dir apache-beam[gcp]==2.43.0

# Copy files from official SDK image, including script/dependencies.
COPY --from=apache/beam_python3.9_sdk /opt/apache/beam /opt/apache/beam

# Perform any additional customizations if desired
COPY ./chromedriver ./chromedriver
COPY ./chromedriver /opt/apache/beam/chromedriver

# Set the entrypoint to Apache Beam SDK launcher.
ENTRYPOINT ["/opt/apache/beam/boot"]
