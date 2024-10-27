import requests
from typing import Dict

def delete_note(
    note_id: int, base_url: str = "http://localhost:37238"
) -> Dict[str, str]:
    """
    Delete a note by sending a DELETE request.

    Args:
        note_id (int): The ID of the note to delete.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        Dict[str, str]: The response from the server as a JSON object indicating the result of the deletion.

    Example:
        >>> delete_note(
                6)
        {"message": "Note deleted successfully"}
    """
    url = f"{base_url}/notes/{note_id}"
    response = requests.delete(url)
    return response.json()
