import requests
import zipfile
import os
import shutil
import json
import logging

logging.basicConfig(level=logging.INFO)

def update_chromedriver():
    version_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    webdriver_dir = "/usr/local/bin"

    try:
        response = requests.get(version_url)
        latest_version_data = json.loads(response.text)
        
        chromedriver_info = next(item for item in latest_version_data["channels"]["Stable"]["downloads"]["chromedriver"] if item["platform"] == "linux64")
        latest_version = latest_version_data["channels"]["Stable"]["version"]
        download_url = chromedriver_info["url"]

        zip_path = os.path.join(webdriver_dir, "chromedriver.zip")
        extracted_folder_path = os.path.join(webdriver_dir, "chromedriver-linux64")

        response = requests.get(download_url)
        with open(zip_path, 'wb') as file:
            file.write(response.content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(webdriver_dir)

        chromedriver_path = os.path.join(webdriver_dir, "chromedriver")
        if os.path.exists(chromedriver_path):
            os.remove(chromedriver_path)

        shutil.move(os.path.join(extracted_folder_path, "chromedriver"), chromedriver_path)

        os.remove(zip_path)
        shutil.rmtree(extracted_folder_path)

        logging.info(f"ChromeDriver updated successfully to version {latest_version}")
    except Exception as e:
        logging.error(f"Error updating ChromeDriver: {e}")

if __name__ == "__main__":
    update_chromedriver()