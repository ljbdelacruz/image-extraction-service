import requests
import os

def scanner_service(access_token, image_data):
    base_url = os.getenv("GATHERER_URL")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-GATHERER-USER-EMAIL': 'lj@metaversegroup.com'
    }
    json = {
        'fileKey': image_data
    }

    try:
        response = requests.post(f"{base_url}/v7/scanner/scan_image", headers=headers, json=json)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        if response.status_code == 201:
            result = response.json()
        else:
            result = {'error': response.text}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise e

    return result