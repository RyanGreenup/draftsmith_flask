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



def build_notes_tree_html(notes_tree: List[NoteTreeModel], fold_level: int = 2) -> str:
    def render_note(note: NoteTreeModel, i: int) -> str:
        if i < fold_level:
            status = "open"
        else:
            status = "closed"

        hyperlink = f'<a href="/note/{note.id}">{note.title}</a>'
        if note.children:
            # Sort the children before rendering them
            note.children.sort(key=lambda x: x.title)
            html = f"<li><details {status}><summary>{hyperlink}</summary>\n<ul>"

            for child in note.children:
                html += render_note(child, i + 1)
            html += "</ul>\n</details>\n</li>"
        else:
            html = f'<li>{hyperlink}</li>'

        return html

    # Sort the top-level notes
    notes_tree.sort(key=lambda x: x.title)

    html = '<ul class="menu bg-base-200 rounded-box w-56">'
    for note in notes_tree:
        html += render_note(note, 0)
    html += "</ul>"

    return html




def get_full_titles(notes_tree: List[NoteTreeModel]) -> Dict[int, str]:
    def traverse_and_build_titles(note: NoteTreeModel, parent_title: str = '') -> Dict[int, str]:
        # Build the full title for the current note
        full_title = f"{parent_title}/{note.title}".strip('/')

        # Prepare the result entry for the current note
        result = {note.id: full_title}

        # Recursively process children, updating the result dictionary
        if note.children:
            for child in note.children:
                result.update(traverse_and_build_titles(child, full_title))

        return result

    # Perform traversal for each root note in the top-level list
    all_full_titles = {}
    for root_note in notes_tree:
        all_full_titles.update(traverse_and_build_titles(root_note))

    return all_full_titles

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


def get_recent_notes(base_url: str = "http://localhost:37238", limit: int = 10) -> List[NoteModel]:
    """
    Retrieve a list of recent notes from the API, sorted by modification date.

    Args:
        base_url (str): The base URL of the API (default: "http://localhost:37238").
        limit (int): The maximum number of notes to retrieve (default: 10).

    Returns:
        List[NoteModel]: A list of recent notes, sorted by modification date.
    """
    url = f"{base_url}/notes"
    response = requests.get(url)
    response.raise_for_status()
    notes_data = response.json()

    adapter = TypeAdapter(List[NoteModel])
    notes = adapter.validate_python(notes_data)

    # Sort notes by modified_at date in descending order
    sorted_notes = sorted(notes, key=lambda x: x.modified_at, reverse=True)

    # Return only the specified number of notes
    return sorted_notes[:limit]

def get_note_backlinks(note_id: int, base_url) -> List[NoteSearchResultModel]:
    """
    Retrieve a list of backlinks for a specific note.

    Args:
        note_id (int): The ID of the note to get backlinks for.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        List[NoteSearchResultModel]: A list of notes that link to the specified note.
    """
    url = f"{base_url}/notes/{note_id}/backlinks"
    response = requests.get(url)
    response.raise_for_status()
    response_data = response.json()

    # Access the "backlinks" key in the response
    backlinks_data = response_data.get("backlinks")

    # Handle case where "backlinks" is None
    if backlinks_data is None:
        print(f"No backlinks found for note {note_id}.")
        return []  # Return an empty list if no backlinks

    # Handle case where "backlinks" is not a list
    if not isinstance(backlinks_data, list):
        print(f"Unexpected backlinks data format: {backlinks_data}")
        return []  # Return an empty list if no backlinks

    try:
        # Assume backlinks_data is a list of dictionaries containing "id" and "title"
        backlinks = [NoteSearchResultModel(**item) for item in backlinks_data]
    except ValidationError as e:
        print(f"Error validating backlinks data: {e}")
        return []  # Return an empty list if validation fails

    return backlinks

def get_note_forward_links(note_id: int, base_url: str = "http://localhost:37238") -> List[NoteSearchResultModel]:
    """
    Retrieve a list of forward links for a specific note.

    Args:
        note_id (int): The ID of the note to get forward links for.
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        List[NoteLinkModel]: A list of notes that the specified note links to.
    """
    url = f"{base_url}/notes/{note_id}/forward-links"
    response = requests.get(url)
    response.raise_for_status()
    response_data = response.json()

    # Access the "forward_links" key in the response
    forward_links_data = response_data.get("forward_links")

    # Handle case where "forward_links" is None
    if forward_links_data is None:
        print(f"No forward links found for note {note_id}.")
        return []  # Return an empty list if no forward links

    # Handle case where "forward_links" is not a list
    if not isinstance(forward_links_data, list):
        print(f"Unexpected forward links data format: {forward_links_data}")
        return []  # Return an empty list if no forward links

    try:
        # Assume forward_links_data is a list of dictionaries containing "id" and "title"
        forward_links = [NoteSearchResultModel(id=item['id'], title=item['title']) for item in forward_links_data]
    except ValidationError as e:
        print(f"Error validating forward links data: {e}")
        return []  # Return an empty list if validation fails

    return forward_links

if __name__ == "__main__":
    tree = get_notes_tree()
    print(json.dumps([item.model_dump() for item in tree], indent=2))
