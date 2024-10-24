from flask import Flask, request
import requests
from typing import List, Dict, Any
from flask import render_template
import os
import json
import markdown
from pydantic import BaseModel, TypeAdapter
from datetime import datetime
import requests
from pprint import pprint

class NoteModel(BaseModel):
   id: int
   title: str
   content: str
   created_at: datetime
   modified_at: datetime

app = Flask(__name__)


# @app.route('/<path:path>')
# def show_path(path):
#     # Prepend a slash to the path to form the correct route
#     full_path = '/' + path
#     full_url = request.url
#
#     s = get_notes()
#
#     message = f"You visited: {full_url} and the route is: {full_path}"
#     message = f"""
# # Draftsmith Web UI
#
# | Current URL | Route |
# | --- | --- |
# | `{full_url}` | `{full_path}` |
#
# # Here are all the notes:
#
#     """
#
#     all_notes = json.dumps(get_notes(), indent=2)
#
#     try:
#         note_matching_title = [note for note in s if note['title'].lower() == path.lower().strip("/")]
#         note = note_matching_title[0]['content']
#         # note = str(note_matching_title) + f"path={path}"
#     except Exception as e:
#         note = f"Path={path} No note found with that title\n\n Error: \n```" + str(e) + "```"
#
#     message += "\n # This Note \n" + "```json\n" + note  + "\n```"
#
#     message += "\n # All the Notes \n" + "```json\n" + all_notes  + "\n```"
#
#     markdown_message = make_html(message)
#     print(markdown_message)
#
#     return markdown_message

def get_note(id: int):
    all_notes = get_notes()
    # Extract the value with the matching id
    note = next((note for note in all_notes if note.id == id), None)
    if note is None:
        # Handle case where note is not found
        # 404
        abort(404)
    return note



@app.route('/')
def root():
    # # Get all the notes
    all_notes = get_notes()
    s = "\n".join([s.title for s in all_notes])
    s = "\n".join([str(note.model_dump()) for note in all_notes])
    s = f"```json\n{s}\n```"
    content = f"# My Notes\n## All Notes in Corpus\n {s}"
    md = make_html(content)
    print(f"Dir: {os.getcwd()}")
    print(f"content: {os.listdir('./src/')}")
    return render_template('base.html', content=md, footer="Bar", all_notes=all_notes)


@app.route('/note/<int:note_id>')
def note_detail(note_id):
   all_notes = get_notes()
   # Logic to fetch and render the specific note based on note_id
   # For example, you might filter the note from `all_notes` or fetch it from a database.
   note = next((note for note in all_notes if note.id == note_id), None)

   if note is None:
       # Handle case where note is not found
       # 404
       abort(404)


   return render_template('note_detail.html', note=note, all_notes=all_notes)



def get_notes(base_url: str = "http://localhost:37238") -> List[NoteModel]:
    """
    Retrieve a list of notes from the API.

    Args:
        base_url (str): The base URL of the API (default: "http://localhost:37238").

    Returns:
        List[Dict[str, Any]]: A list of notes, each represented as a dictionary.

    Example:
        >>> get_notes()
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



def make_html(text: str) -> str:
    html_body = markdown.markdown(
        text,
        extensions=[
            "attr_list",
            # "markdown_captions",
            "def_list",
            "nl2br",
            "toc",
            "sane_lists",
            "pymdownx.tasklist",
            "pymdownx.inlinehilite",
            "pymdownx.blocks.tab",
            "abbr",
            "md_in_html",
            "markdown_gfm_admonition",
            "codehilite",
            "fenced_code",
            "tables",
            "pymdownx.superfences",
            "pymdownx.blocks.details",
            "admonition",
            "toc",
            # TODO Make base_url configurable to share between preview and editor
            # WikiLinkExtension(base_url=os.getcwd() + os.path.sep, end_url=".md"),
            "md_in_html",
            "footnotes",
            "meta",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "linenums": False,
                "guess_lang": False,
            }
        },
    )

    # return f"<div class='markdown'>{html_body}</div>"
    return html_body



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



