import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv("URL_BASE")


def upload_pdf(file):
    url = f"{URL_BASE}/upload-pdf/"
    files = {'file': file}
    response = requests.post(url, files=files)
    return response.json()


def get_related_documents(title, number):
    url = f"{URL_BASE}/related_documents/"
    data = {"title": title, "number":number}
    response = requests.post(url, json=data)
    return response.json()