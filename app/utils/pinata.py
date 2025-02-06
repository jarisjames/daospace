import requests
from django.conf import settings

def upload_to_pinata(file_path, metadata):
    """Uploads a file and metadata to Pinata and returns the IPFS hash."""
    url_file = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    url_json = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    headers = {
        "Authorization": f"Bearer {settings.PINATA_JWT}",
    }

    # Upload the GLB file
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url_file, headers=headers, files=files)
        response.raise_for_status()  # Ensure no silent errors
        glb_hash = response.json()["IpfsHash"]

    # Add GLB file hash to metadata
    metadata["glb"] = f"ipfs://{glb_hash}"

    # Upload metadata JSON
    response = requests.post(url_json, headers=headers, json=metadata)
    response.raise_for_status()  # Ensure no silent errors
    return response.json()["IpfsHash"]
