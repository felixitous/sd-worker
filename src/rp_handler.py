import time

import runpod
import requests
from requests.adapters import HTTPAdapter, Retry

LOCAL_URL = "http://127.0.0.1:3000/sdapi/v1"
BASE_URL = "http://127.0.0.1:3000"

automatic_session = requests.Session()
retries = Retry(total=10, backoff_factor=0.1, status_forcelist=[502, 503, 504])
automatic_session.mount("http://", HTTPAdapter(max_retries=retries))


# ---------------------------------------------------------------------------- #
#                              Automatic Functions                             #
# ---------------------------------------------------------------------------- #
def wait_for_service(url):
    """
    Check if the service is ready to receive requests.
    """
    while True:
        try:
            requests.get(url, timeout=120)
            return
        except requests.exceptions.RequestException:
            print("Service not ready yet. Retrying...")
        except Exception as err:
            print("Error: ", err)

        time.sleep(0.2)


def run_controlnet(controlnet_request):
    """
    Run inference on a request.
    """
    response = automatic_session.get(
        url=f"{BASE_URL}/controlnet/{controlnet_request}", timeout=600
    )
    return response.json()


def run_inference(inference_request):
    """
    Run inference on a request.
    """
    if inference_request.get("action") == "controlnet":
        return run_controlnet(inference_request["command"])
    response = automatic_session.post(
        url=f"{LOCAL_URL}/txt2img", json=inference_request, timeout=600
    )
    return response.json()


def run_controlnet(controlnet_request):
    """
    Run inference on a request.
    """
    response = automatic_session.get(
        url=f"{BASE_URL}/controlnet/{controlnet_request}", timeout=600
    )
    return response.json()


# ---------------------------------------------------------------------------- #
#                                RunPod Handler                                #
# ---------------------------------------------------------------------------- #
def handler(event):
    """
    This is the handler function that will be called by the serverless.
    """
    json = run_inference(event["input"])
    # return the output that you want to be returned like pre-signed URLs to output artifacts
    return json


if __name__ == "__main__":
    wait_for_service(url=f"{LOCAL_URL}/txt2img")

    print("WebUI API Service is ready. Starting RunPod...")

    runpod.serverless.start({"handler": handler})
