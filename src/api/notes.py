import requests
from flask import abort
from typing import List
from pydantic import BaseModel, TypeAdapter
from datetime import datetime


class NoteModel(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    modified_at: datetime


# TODO base_url should be an argument for the CLI
def get_notes(base_url: str = "http://localhost:37238") -> List[NoteModel]:
    """
    Retrieve a list of notes from the API.

    Args:
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        List[Dict[str, Any]]: A list of notes, each represented as a dictionary.

    Example:
        >>> get_notes().model_dump()
        [
          {
            "id": 1,
            "title": "First note",
            "content": "This is the first note in the system.",
            "created_at": "2024-10-20T05:04:42.709064Z",
            "modified_at": "2024-10-20T05:04:42.709064Z"
          },
          {
            "id": 2,
            "title": "Foo",
            "content": "This is the updated content of the note.",
            "created_at": "2024-10-20T05:04:42.709064Z",
            "modified_at": "2024-10-20T05:15:03.334779Z"
          },
          ...
        ]
    """
    url = f"{base_url}/notes"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    notes_data = response.json()

    # Validate and parse the data using TypeAdapter
    adapter = TypeAdapter(List[NoteModel])
    notes = adapter.validate_python(notes_data)
    print(repr(notes))

    return notes


def get_note(all_notes: List[NoteModel], note_id: int) -> NoteModel:
    all_notes = get_notes()
    # Logic to fetch and render the specific note based on note_id
    # For example, you might filter the note from `all_notes` or fetch it from a database.
    note = next((note for note in all_notes if note.id == note_id), None)

    if note is None:
        # Handle case where note is not found
        # 404
        abort(404)

    return note
