from datetime import datetime
from flask import abort
from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic import ValidationError
from typing import List, Optional
import json
import requests
from typing import List
import requests
from urllib.parse import quote
from pydantic import ValidationError
from pydantic import BaseModel
from typing import List


class NoteSearchResultModel(BaseModel):
    id: int
    title: str


class NoteTreeModel(BaseModel):
    id: int
    title: str
    type: Optional[str] = ""  # Assuming type is a string and can be empty
    children: Optional[List["NoteTreeModel"]] = None

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
def get_notes(base_url: str = "http://localhost:37238", ids: List[int] | None = None) -> List[NoteModel]:
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

    if ids:
        notes = [note for note in notes if note.id in ids]

    return notes


# TODO this should use an api endpoint to fetch a single note
# TODO there should be an API endpoint to fetch the tree of titles and that's all
def get_note(note_id: int) -> NoteModel:
    all_notes = get_notes()
    # Logic to fetch and render the specific note based on note_id
    # For example, you might filter the note from `all_notes` or fetch it from a database.
    note = next((note for note in all_notes if note.id == note_id), None)

    if note is None:
        # Handle case where note is not found
        # 404
        abort(404)

    return note


def build_notes_tree_html(notes_tree: List[NoteTreeModel]) -> str:
    def render_note(note: NoteTreeModel) -> str:
        if note.children:
            html = f"<li>\n<details open>\n<summary>{note.title}</summary>\n<ul>"
            for child in note.children:
                html += render_note(child)
            html += "</ul>\n</details>\n</li>"
        else:
            html = f'<li><a href="/note/{note.id}">{note.title}</a></li>'
        return html

    html = '<ul class="menu bg-base-200 rounded-box w-56">'
    for note in notes_tree:
        html += render_note(note)
    html += "</ul>"

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


def find_note_path(
    notes_tree: List[NoteTreeModel],
    target_id: int,
    current_path: Optional[List[NoteTreeModel]] = None
) -> Optional[List[NoteTreeModel]]:
    if current_path is None:
        current_path = []

    for note in notes_tree:
        new_path = current_path + [note]
        if note.id == target_id:
            return new_path
        if note.children:
            result = find_note_path(note.children, target_id, new_path)
            if result:
                return result
    return None



def search_notes(
    query: str, base_url: str = "http://localhost:37238"
) -> List[NoteSearchResultModel]:
    """
    Search for notes based on a query string by sending a GET request.

    Args:
        query (str): The search query string.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        List[NoteSearchResultModel]: A list of notes that match the search criteria.

    Example json Response:
        >>> search_notes("updated content")
        [NoteSearchResultModel(id=2, title="Foo")]
    """
    encoded_query = quote(query)
    url = f"{base_url}/notes/search?q={encoded_query}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    search_results_data = response.json()

    try:
        # Validate and parse the search results
        if search_results_data:
            search_results = [NoteSearchResultModel.model_validate(item) for item in search_results_data]
        else:
            search_results = []
    except ValidationError as e:
        # Handle validation error
        print(f"Error validating data: {e}")
        raise

    return search_results


if __name__ == "__main__":
    tree = get_notes_tree()
    print(json.dumps([item.model_dump() for item in tree], indent=2))
