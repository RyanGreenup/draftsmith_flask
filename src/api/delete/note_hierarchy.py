import requests
from typing import Dict, Any, List
from urllib.parse import quote
from typing import Dict, Any
import requests

def delete_note_hierarchy(
    note_id: int, base_url: str = "http://localhost:37238"
) -> Dict[str, Any]:
    """
    Delete the hierarchy entry of a note by sending a DELETE request.

    Args:
        note_id (int): The ID of the note whose hierarchy is to be deleted.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        Dict[str, Any]: The response from the server as a JSON object.

    Example:
        >>> delete_note_hierarchy(2)
        {"message":"Note hierarchy entry deleted successfully"}
    """
    url = f"{base_url}/notes/hierarchy/{note_id}"

    response = requests.delete(url)
    response.raise_for_status()

    return response.json()


