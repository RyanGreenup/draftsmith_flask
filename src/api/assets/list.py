from urllib.parse import quote
from typing import Optional
from pydantic import BaseModel, ValidationError
import requests
from datetime import datetime
from typing import List


class AssetModel(BaseModel):
    id: int
    file_name: str
    asset_type: str
    description: str
    created_at: datetime


def get_assets(base_url: str) -> List[AssetModel]:
    """
    Retrieve a list of assets from the API.

    Args:
        base_url (str): The base URL of the API (e.g., "http://localhost:37238").

    Returns:
        List[AssetModel]: A list of asset models parsed from the API response.
    """
    url = f"{base_url}/assets"
    try:
        # Make a GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the response is bad
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

    try:
        # Parse and validate the response using Pydantic
        asset_data = response.json()
        assets = [AssetModel(**asset) for asset in asset_data]
        return assets
    except ValidationError as ve:
        print(f"Validation error: {ve}")
    except ValueError as e:
        print(f"Error parsing JSON: {e}")

    return []




class AssetIDModel(BaseModel):
    id: int


def get_asset_id(base_url: str, filename: str) -> Optional[int]:
    """
    Retrieve the asset ID corresponding to the given filename.

    Args:
        base_url (str): The base URL of the API (e.g., "http://localhost:37238").
        filename (str): The filename to query the asset ID for.

    Returns:
        Optional[int]: The asset ID if found, otherwise None.
    """
    # Construct the query URL, ensuring the filename is properly encoded
    url = f"{base_url}/assets/id?filename={quote(filename)}"
    try:
        # Make the GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    # Parse and validate the response using Pydantic
    try:
        asset_data = response.json()
        asset = AssetIDModel(**asset_data)
        return asset.id
    except ValidationError as ve:
        print(f"Validation error: {ve}")
    except ValueError as e:
        print(f"Error parsing JSON: {e}")

    return None


# Example Usage
if __name__ == "__main__":
    # Getting id of the asset
    # Assuming the service is running locally and the port is 37238
    base_url = "http://localhost:37238"

    # Test with filenames
    filenames = ["README.md", "README_1.md", "uploads/README.md"]
    for filename in filenames:
        asset_id = get_asset_id(base_url, filename)
        if asset_id is not None:
            print(f"The asset ID for '{filename}' is {asset_id}.")
        else:
            print(f"Asset ID for '{filename}' not found.")

    # Listing all files
    base_url = "http://localhost:37238"
    assets = get_assets(base_url)
    for asset in assets:
        print(asset.json())

