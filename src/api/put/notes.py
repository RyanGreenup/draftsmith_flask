from datetime import datetime
from flask import abort
from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic import ValidationError
from typing import List, Optional
import json
import requests
from typing import List, Dict
import requests
from urllib.parse import quote
from pydantic import ValidationError
from pydantic import BaseModel
from typing import List, Any












# TODO better names
def update_server_note(
    note_id: int, title: Optional[str] = None, content: Optional[str] = None, base_url: str = "http://localhost:37238"
) -> Dict[str, Any]:
    """
    Update the details of a note by sending a PUT request.

    Args:
        note_id (int): The ID of the note to update.
        title (Optional[str]): The new title of the note.
        content (Optional[str]): The new content of the note.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        Dict[str, Any]: The response from the server as a JSON object.

    Example:
        >>> update_note(
                1, title="New Title")
        {"id": 1, "message": "Note updated successfully"}
    """
    update_data = {}
    if title is not None:
        update_data['title'] = title
    if content is not None:
        update_data['content'] = content

    url = f"{base_url}/notes/{note_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, json=update_data, headers=headers)
    return response.json()

