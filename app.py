import sys
import requests
import argparse
import time
import traceback
from contextlib import suppress
from prometheus_client import start_http_server, Gauge, REGISTRY

# Remove the default metrics
for name in list(REGISTRY._names_to_collectors.values()):
    with suppress(KeyError):
        REGISTRY.unregister(name)


# Create metrics
SERVICE_UP = Gauge('sample_external_url_up', 'URL Up', ['url'])
SERVICE_LATENCY = Gauge('sample_external_url_response_ms', 'Response Time', ['url'])


# Process the request for a URL
def check_url(url):
    """Checks if a URL is up and track the response time by sending HTTP GET request.

    Args:
        url (str): The URL to be checked.

    Returns:
        A 2-tuple of two numbers (floats), i.e. (URL status, response time).
        URL status: 1 if the URL is up, otherwise 0.
        Response time: response time in milliseconds.
    """
    try:
        request_time = time.time()
        
        response = requests.get(url, timeout=5)


        response_time = time.time() - request_time

        # Check the status code of the response
        if response.status_code == 200:
            url_status = 1
        else:
            # if status code is not 200
            url_status = 0

    except requests.exceptions.Timeout:
        # Print out the traceback, so that the exception won't be silenced.
        traceback.print_exc()
        # Service is considered as down if timeout
        url_status = 0
        # Set response time to Inf to indicate timeout
        response_time = float('inf')
    
    # Save the URL status
    SERVICE_UP.labels(url).set(url_status)
    # Save response time in milliseconds
    response_time_ms = response_time * 1000
    SERVICE_LATENCY.labels(url).set(response_time_ms)

    return url_status, response_time_ms

def uptime_check(delay=1):
    urls = ["https://httpstat.us/503", "https://httpstat.us/200"]
    url_status = {}

    for url in urls:
        url_status[url] = check_url(url)[0]
        time.sleep(delay)
    return url_status

def parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Uptime check service arguments.")
    parser.add_argument('delay', type=int, nargs='?', help="Time interval between two uptime checks in seconds.")
    args = parser.parse_args(argv)
    if args.delay:
        return args.delay
    return 1


# This is the main function
# This following lines are not tested due to the infinite loop
if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(80)
    # Generate some requests.
    while True:
        uptime_check(parse_arguments(sys.argv[1:]))
