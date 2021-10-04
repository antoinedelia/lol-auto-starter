import os
import requests

API_URL = "http://api.pushingbox.com/pushingbox"
DEV_ID = os.getenv("PUSHING_BOX_DEV_ID")


def send_pushingbox_notification(msg: str, method="GET"):
    params = (
        ('devid', DEV_ID),
        ('msg', msg),
    )
    requests.request(method=method, url=API_URL, params=params)
