import requests
from typing import Dict, Any

def create_note_hierarchy(
    parent_note_id: int,
    child_note_id: int,
    hierarchy_type: str,
    base_url: str = "http://localhost:37238"
) -> Dict[str, Any]:
    """
    Create a note hierarchy entry by sending a POST request.

    Args:
        parent_note_id (int): The ID of the parent note.
        child_note_id (int): The ID of the child note.
        hierarchy_type (str): The type of hierarchy (e.g., "subpage").
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        Dict[str, Any]: The response from the server as a JSON object.

    Example:
        >>> create_note_hierarchy(1, 2, "subpage")
        {"id": 2, "message": "Note hierarchy entry added successfully"}
    """
    url = f"{base_url}/notes/hierarchy"
    hierarchy_data = {
        "parent_note_id": parent_note_id,
        "child_note_id": child_note_id,
        "hierarchy_type": hierarchy_type
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=hierarchy_data, headers=headers)
    response.raise_for_status()
    return response.json()


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
    return response.json()

def update_note_hierarchy(
    parent_note_id: int,
    child_note_id: int,
    hierarchy_type: str,
    base_url: str = "http://localhost:37238"
) -> Dict[str, Any]:
    """
    Update the note hierarchy by first attempting to delete the current hierarchy,
    then creating a new one.

    Args:
        parent_note_id (int): The ID of the parent note.
        child_note_id (int): The ID of the child note.
        hierarchy_type (str): The type of hierarchy (e.g., "subpage").
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        Dict[str, Any]: The response from the server for the create operation.
    """
    try:
        # Attempt to delete the current hierarchy
        delete_response = delete_note_hierarchy(child_note_id, base_url)
        print(f"Delete response: {delete_response}")
    except Exception as e:
        # Log the exception but do not stop the creation process
        print(f"Deletion failed with error: {e}")

    # Create the new note hierarchy
    create_response = create_note_hierarchy(parent_note_id, child_note_id, hierarchy_type, base_url)

    return create_response
