import requests
from typing import Dict, Any

from typing import Optional

def update_note_hierarchy(
    note_id: int,
    parent_note_id: Optional[int] = None,
    hierarchy_type: Optional[str] = None,
    base_url: str = "http://localhost:37238",
) -> Dict[str, Any]:
    """
    Update the hierarchy of a note by sending a PUT request.

    Args:
        note_id (int): The ID of the note to update hierarchy for.
        parent_note_id (Optional[int]): The ID of the parent note (if applicable).
        hierarchy_type (Optional[str]): The type of hierarchy (e.g., "subpage").
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        Dict[str, Any]: The response from the server as a JSON object.

    Example:
        >>> update_note_hierarchy(4, parent_note_id=2, hierarchy_type="subpage")
        {"message": "Note hierarchy entry updated successfully"}
    """
    url = f"{base_url}/notes/hierarchy/{note_id}"

    # Construct the hierarchy data
    hierarchy_data = {}
    if parent_note_id is not None:
        hierarchy_data['parent_note_id'] = parent_note_id
    if hierarchy_type is not None:
        hierarchy_data['hierarchy_type'] = hierarchy_type

    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=hierarchy_data, headers=headers)
    response.raise_for_status()
    return response.json()

