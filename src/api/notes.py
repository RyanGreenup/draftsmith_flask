import json
import requests
from flask import abort
from typing import List
from pydantic import BaseModel, TypeAdapter
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class NoteTreeModel(BaseModel):
    id: int
    title: str
    type: Optional[str] = ""  # Assuming type is a string and can be empty
    children: Optional[List['NoteTreeModel']] = None

    class Config:
        # For nested/recursive models, this is necessary
        from_attributes = True


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

from typing import List
import requests
from pydantic import ValidationError

def build_notes_tree_html(notes_tree: List[NoteTreeModel]) -> str:
    def render_note(note: NoteTreeModel) -> str:
        html = f'<li><a href="/note/{note.id}">{note.title}</a>'

        if note.children:
            html += '\n<details open>\n<summary>\n<ul>'
            for child in note.children:
                html += render_note(child)
            html += '</ul>\n</summary>\n</details>'

        html += '</li>'
        return html

    html = '<ul>'
    for note in notes_tree:
        html += render_note(note)
    html += '</ul>'

    return html

def get_notes_tree(base_url: str = "http://localhost:37238") -> List[NoteTreeModel]:
    """
    Retrieve the notes tree by sending a GET request.

    Args:
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        List[NoteTreeModel]: The parsed and validated response from the server.

    Example json Response:
        >>> get_notes_tree().model_dump()
        [
          {
            "id": 3,
            "title": "Foo",
            "type": ""
          },
          {
            "id": 4,
            "title": "New Note Title",
            "type": ""
          },
          {
            "id": 1,
            "title": "First note",
            "type": "",
            "children": [
              {
                "id": 2,
                "title": "Foo",
                "type": "subpage"
              },
            ]
          }
        ]
    """
    url = f"{base_url}/notes/tree"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    notes_tree_data = response.json()

    try:
        # Validate and parse the data as a list of NoteTreeModel
        notes_tree = [NoteTreeModel.model_validate(item) for item in notes_tree_data]
    except ValidationError as e:
        # Handle validation error
        print(f"Error validating data: {e}")
        raise

    return notes_tree


if __name__ == '__main__':
    tree = get_notes_tree()
    print(json.dumps([item.model_dump() for item in tree], indent=2))
