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






from typing import Any
import requests

def create_note(url: str, title: str|None, content: str|None) -> Dict[str, Any]:
    """
    Create a new note by sending a POST request to the specified URL.

    Args:
        url (str): The full URL to send the POST request to.
        title (str): The title of the note.
        content (str): The content of the note.

    Returns:
        Dict[str, Any]: The response from the server as a JSON object.

    Example:
        >>> create_note(
            "http://localhost:37238/notes",
            "New Note Title",
            "This is the content of the new note.")

        {"id":4,"message":"Note created successfully"}
    """

    note_data = {}
    if title is not None:
        note_data['title'] = title
    if content is not None:
        note_data['content'] = content
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=note_data, headers=headers)
    return response.json()

import requests
from typing import Dict, Any, Optional

def create_note(url: str, title: str|None, content: str|None) -> Dict[str, Any]:
    data = {
        "title": title,
        "content": content
    }
    response = requests.post(f"{url}/notes", json=data)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        # If the response is not valid JSON, return the text content
        return {"error": "Invalid JSON response", "content": response.text}
