from pydantic import BaseModel
from typing import Optional
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os

class UploadResponseModel(BaseModel):
    filename: str
    id: int
    message: str

def upload_file(file_path: str, description: Optional[str] = None, base_url: str = "http://localhost:37238") -> UploadResponseModel:
    """
    Upload a file to the API.

    Args:
        file_path (str): The path to the file to be uploaded.
        description (Optional[str]): An optional description of the file.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        UploadResponseModel: The parsed and validated response from the server.

    Raises:
        requests.exceptions.RequestException: If there's an error with the request.
        ValueError: If the file doesn't exist.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    url = f"{base_url}/upload"

    # Prepare the multipart form data
    fields = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'))
    }
    if description:
        fields['description'] = description

    multipart_data = MultipartEncoder(fields=fields)

    headers = {
        'Content-Type': multipart_data.content_type
    }

    response = requests.post(url, data=multipart_data, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse and validate the response using Pydantic
    upload_response = UploadResponseModel.model_validate(response.json())

    return upload_response

if __name__ == "__main__":
    # Example usage
    try:
        result = upload_file("/path/to/your/file.txt", description="Sample upload")
        print(result.model_dump())
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
    except ValueError as e:
        print(f"Invalid input: {e}")
