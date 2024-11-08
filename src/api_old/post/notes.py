import requests
from typing import Dict
from typing import Any







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

from typing import Dict, Any

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
