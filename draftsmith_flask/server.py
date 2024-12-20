#!/usr/bin/env python
from datetime import datetime
from api import (
    TreeNote,
    Note,
    UpdateNoteRequest,
    Tag,
    TreeTag,
    TreeTagWithNotes,
    NoteWithoutContent,
)
from api import NoteAPI, TagAPI, TaskAPI, AssetAPI
from flask import (
    Flask,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    jsonify,
)
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup
from typing import List, Optional, Dict
import os
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Inherit the API base URL from the environment variables
API_SCHEME = os.environ.get("API_SCHEME")
API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")
API_BASE_URL = f"{API_SCHEME}://{API_HOST}:{API_PORT}"

# Initialize the API clients
noteapi = NoteAPI(base_url=API_BASE_URL)
tagapi = TagAPI(base_url=API_BASE_URL)
taskapi = TaskAPI(base_url=API_BASE_URL)
assetsapi = AssetAPI(base_url=API_BASE_URL)


# BEGIN: API functions that should be implemented by server
def get_recent_notes(limit: int = 10) -> List[Note]:
    notes = noteapi.get_all_notes()
    # Sort the notes by the last modified date, using a minimum datetime for None values
    notes.sort(key=lambda x: x.modified_at or datetime.min, reverse=True)
    return notes[:limit]


def get_full_titles(notes_tree: List[TreeNote]) -> Dict[int, str]:
    def traverse_and_build_titles(
        note: TreeNote, parent_title: str = ""
    ) -> Dict[int, str]:
        # Build the full title for the current note
        full_title = f"{parent_title}/{note.title}".strip("/")

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


def find_note_path(
    notes_tree: List[TreeNote],
    target_id: int,
    current_path: Optional[List[TreeNote]] = None,
) -> Optional[List[TreeNote]]:
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


def get_notes(ids: List[int] | None = None) -> List[Note]:
    notes = noteapi.get_all_notes()
    # Filter notes by ID if specified
    if ids:
        notes = [note for note in notes if note.id in ids]
    return notes


# END: API functions that should be implemented by server

app = Flask(__name__)
app.secret_key = os.getenv("CSRF_SECRET_KEY")
csrf = CSRFProtect(app)
app.config["WTF_CSRF_ENABLED"] = True

folder_svg = """<svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="1.5"
      stroke="currentColor"
      class="h-5 w-5 md:h-4 md:w-4">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
    </svg>"""

tag_svg = """<svg
  xmlns="http://www.w3.org/2000/svg"
  fill="none"
  viewBox="0 0 24 24"
  stroke-width="1.5"
  stroke="currentColor"
  class="h-5 w-5 md:h-4 md:w-4">
  <path
    stroke-linecap="round"
    stroke-linejoin="round"
    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z" />
</svg>"""

file_svg = """<svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    stroke-width="1.5"
    stroke="currentColor"
    class="h-4 w-4">
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
  </svg>"""


def build_tags_tree_html(
    tags_tree: List[TreeTagWithNotes], note_id: int | None = None
) -> str:
    def render_tag(tag: TreeTagWithNotes) -> str:
        # Initialize classes list for all tags
        classes = ["tag-item"]

        # Add highlighting classes if this is the current tag
        if tag.id == note_id:
            classes.extend(
                ["bg-blue-100", "text-blue-800", "font-semibold", "rounded-md"]
            )

        class_str = " ".join(classes)
        tag_link = f'{tag_svg}<a href="/tags/{tag.id}">{tag.name}</a>'

        if tag.children or tag.notes:
            # Create details element for hierarchical structure
            html = [f'<li class="{class_str}" data-tag-id="{tag.id}">']
            html.append(
                "<details open>"
            )  # Always open by default since we don't want folding
            html.append(f"<summary>{tag_link}</summary>")
            html.append('<ul class="ml-4">')  # Indentation for nested items

            # First add child tags (if any)
            if tag.children:
                sorted_children = sorted(tag.children, key=lambda x: x.name)
                for child in sorted_children:
                    html.append(render_tag(child))

            # Then add notes (if any)
            if tag.notes:
                sorted_notes = sorted(tag.notes, key=lambda x: x.title)
                for note in sorted_notes:
                    note_link = f'{file_svg}<a href="/note/{note.id}">{note.title}</a>'
                    html.append(f'<li class="note-item">{note_link}</li>')

            html.append("</ul>")
            html.append("</details>")
            html.append("</li>")
        else:
            # For tags without children or notes, just render the tag
            html = [f'<li class="{class_str}">{tag_link}</li>']

        return "\n".join(html)

    # Sort top-level tags
    sorted_tags = sorted(tags_tree, key=lambda x: x.name)

    html = ['<ul class="menu bg-base-200 rounded-box w-full md:w-56">']
    for tag in sorted_tags:
        html.append(render_tag(tag))
    html.append("</ul>")

    return "\n".join(html)


def build_notes_tree_html(
    notes_tree: List[TreeNote], fold_level: int = 2, note_id: int | None = None
) -> str:
    file_svg = """<svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="h-5 w-5 md:h-4 md:w-4">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>"""

    def find_parent_ids(
        tree: List[TreeNote], target_id: int, path: set[int] = None
    ) -> set[int]:
        if path is None:
            path = set()

        for note in tree:
            if note.id == target_id:
                return path
            if note.children:
                child_path = find_parent_ids(note.children, target_id, path | {note.id})
                if child_path is not None:
                    return child_path
        return None

    parent_ids = (
        set() if note_id is None else (find_parent_ids(notes_tree, note_id) or set())
    )

    def render_note(
        note: TreeNote, depth: int = 0, parent_of_current: bool = False
    ) -> str:
        svg = file_svg if not note.children else folder_svg

        # Determine if this note should be open
        should_open = (
            note.id in parent_ids  # Open if it's a parent of current note
            or note.id == note_id  # Open if it's the current note
            or (
                parent_of_current and depth < fold_level
            )  # Open if under current note within fold_level
        )

        status = "open" if should_open else "closed"

        # Initialize classes list for all notes
        classes = ["note-item"]

        # Add highlighting classes if this is the current note
        if note.id == note_id:
            classes.extend(
                ["bg-blue-100", "text-blue-800", "font-semibold", "rounded-md"]
            )

        class_str = " ".join(classes)
        hyperlink = f'{svg}<a href="/note/{note.id}">{note.title}</a>'

        if note.children:
            # Sort the children before rendering them
            note.children.sort(key=lambda x: x.title)

            # Determine if children are under the current note
            is_current = note.id == note_id

            html = f'<li class="{class_str}" draggable="true" data-note-id="{note.id}"><details {status}><summary>{hyperlink}</summary>\n<ul>'

            for child in note.children:
                html += render_note(child, depth + 1, is_current)
            html += "</ul>\n</details>\n</li>"
        else:
            html = f'<li class="{class_str}" draggable="true" data-note-id="{note.id}">{hyperlink}</li>'

        return html

    # Sort the top-level notes
    notes_tree.sort(key=lambda x: x.title)

    html = '<ul class="menu bg-base-200 rounded-box w-full md:w-56">'
    for note in notes_tree:
        html += render_note(note, 0)
    html += "</ul>"

    return html


@app.context_processor
def inject_all_notes():
    return dict(all_notes=get_notes())


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


def add_cache_control_header(response):
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000"
    return response


app.after_request(add_cache_control_header)


@app.route("/")
def root():
    # return redirect(url_for("note_detail", note_id=1))
    # Redirect to recent pages
    return redirect(url_for("recent_pages"))


@app.context_processor
def inject_tag_sidebar():
    tags_tree = tagapi.get_tags_tree()
    tag_html = Markup(build_tags_tree_html(tags_tree))
    return dict(tag_html=tag_html)


@app.route("/tags/<int:tag_id>")
def tag_detail(tag_id: int):
    notes = get_tag_notes(tag_id)
    tag = tagapi.get_tag(tag_id)
    return render_template("tagged_pages_list.html", notes=notes, tag=tag)


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    note = noteapi.get_note(note_id)
    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree, note_id=note_id)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    # Get backlinks for the current note
    backlinks = noteapi.get_note_backlinks(note_id)
    forwardlinks = noteapi.get_note_forward_links(note_id)

    # Get tags (TODO this needs an endpoint)

    note_tags = tagapi.get_note_tag_relations()
    tags = [tagapi.get_tag(nt.tag_id) for nt in note_tags if nt.note_id == note_id]

    # Parse the markdown content
    html_content = noteapi.get_rendered_note(note_id, format="html")

    return render_template(
        "note_detail.html",
        note=note,
        note_html=html_content,
        tree_html=tree_html,
        note_path=note_path or [],
        backlinks=backlinks,
        forwardlinks=forwardlinks,
        tags=tags,
    )


def get_note_tags(note_id) -> List[Tag]:
    note_tags = tagapi.get_note_tag_relations()
    tags = [tagapi.get_tag(nt.tag_id) for nt in note_tags if nt.note_id == note_id]
    return tags


def get_tag_notes(tag_id) -> List[NoteWithoutContent]:
    note_tags = tagapi.get_note_tag_relations()
    relevant_note_tags = [nt for nt in note_tags if nt.tag_id == tag_id]
    all_note_details = [
        noteapi.get_note_without_content(nt.note_id) for nt in relevant_note_tags
    ]
    return all_note_details


@app.context_processor
def inject_backlinks():
    def get_backlinks_for_current_note():
        if "note_id" in request.view_args:
            note_id = request.view_args["note_id"]
            return noteapi.get_note_backlinks(note_id)
        return []

    return dict(backlinks=get_backlinks_for_current_note())


@app.route("/edit/<int:note_id>")
def edit_note(note_id):
    note = noteapi.get_note(note_id)
    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree, note_id=note_id)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)
    html_content = noteapi.get_rendered_note(note_id, format="html")

    return render_template(
        "note_edit.html",
        note=note,
        note_html=html_content,
        tree_html=tree_html,
        note_path=note_path or [],
    )


@app.route("/notes/create", methods=["GET", "POST"])
@app.route("/notes/create/<int:parent_id>", methods=["GET", "POST"])
def create_note_page(parent_id=None):
    if request.method == "GET":
        print(f"DEBUG: Received GET request with parent_id: {parent_id}")  # Debug log
        notes_tree = noteapi.get_notes_tree()
        tree_html = build_notes_tree_html(notes_tree, note_id=parent_id)
        tree_html = Markup(tree_html)

        return render_template("note_create.html", tree_html=tree_html, title="", parent_id=parent_id)
    elif request.method == "POST":
        print(f"DEBUG: Received POST request with parent_id: {parent_id}")  # Debug log
        content = request.form.get("content")
        title = request.form.get("title")
        try:
            # First create the note
            response = noteapi.note_create(title=title or "", content=content or "")
            print(f"DEBUG: Created note with response: {response}")  # Debug log

            if "error" in response:
                flash(f"Error creating note: {response['error']}", "error")
                return redirect(url_for("create_note_page"))

            new_note_id = response.get("id")
            if new_note_id:
                # If parent_id is provided, attach the new note as a child
                if parent_id:
                    print(f"DEBUG: Attempting to attach note {new_note_id} to parent {parent_id}")  # Debug log
                    try:
                        noteapi.attach_note_to_parent(
                            child_note_id=new_note_id, parent_note_id=parent_id
                        )
                        print("DEBUG: Successfully attached note to parent")  # Debug log
                        flash("Note created and attached to parent successfully", "success")
                    except requests.exceptions.RequestException as e:
                        print(f"DEBUG: Failed to attach note to parent: {str(e)}")  # Debug log
                        flash(
                            f"Note created but failed to attach to parent: {str(e)}",
                            "warning"
                        )
                return redirect(url_for("note_detail", note_id=new_note_id))
            else:
                flash("Error creating note: No ID returned", "error")
                return redirect(url_for("create_note_page"))
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Error creating note: {str(e)}")  # Debug log
            flash(f"Error creating note: {str(e)}", "error")
            return redirect(url_for("create_note_page"))


# TODO Implement title
@app.route("/edit/<int:note_id>", methods=["POST", "PUT"])
def update_note(note_id):
    title = request.form.get("title")
    content = request.form.get("content")
    if request.method == "POST":
        _note = noteapi.update_note(
            note_id, UpdateNoteRequest(title=title, content=content)
        )
        # Refresh the page to show the updated note
    elif request.method == "PUT":
        noteapi.note_create(title=title or "", content=content or "")
        _note = noteapi.update_note(
            note_id, UpdateNoteRequest(title=title, content=content)
        )
        # Refresh the page to show the updated note
    return redirect(url_for("note_detail", note_id=note_id))


@app.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return redirect(url_for("root"))

    # TODO maybe API should include a field with and withot the full name to
    # Save multiple requests?
    search_results = noteapi.search_notes(query)
    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree, note_id=None)
    tree_html = Markup(tree_html)

    ids = [n.id for n in search_results]
    full_titles = get_full_titles(notes_tree)

    # TODO this should return the tree and construct the nested title
    # Maybe regail this to the server?
    search_results = []
    for note_id in ids:
        note = noteapi.get_note(note_id)
        html_content = noteapi.get_rendered_note(note.id, format="html")
        search_result = {
            "id": note.id,
            "title": full_titles[note.id],
            "content": f"<div>{html_content[:200]}</div> ...",
            "tags": get_note_tags(note.id),
        }
        search_results.append(search_result)

    return render_template(
        "note_search.html",
        query=query,
        search_results=search_results,
        tree_html=tree_html,
        note=None,
    )


@app.route("/note/<int:note_id>/delete", methods=["POST"])
def delete_note_page(note_id):
    try:
        noteapi.delete_note(note_id)
        flash("Note deleted successfully", "success")
        return redirect(url_for("root"))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            flash("Note not found", "danger")
        else:
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("note_detail", note_id=note_id))
    except requests.exceptions.RequestException as e:
        flash(f"Error deleting note: {str(e)}", "error")
        return redirect(url_for("note_detail", note_id=note_id))


@app.route("/note/<int:note_id>/detach", methods=["POST"])
def detach_note(note_id):
    try:
        noteapi.detach_note_from_parent(note_id)
        flash("Note detached successfully", "success")
    except requests.exceptions.HTTPError as e:
        handle_http_error(e)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for("note_detail", note_id=note_id))


@app.route("/note/<int:note_id>/move", methods=["GET", "POST"])
def move_note(note_id):
    if request.method == "GET":
        return render_template("move_note.html", note_id=note_id)

    new_parent_id = request.form.get("new_parent_id")
    if not new_parent_id:
        flash("Please provide a parent ID", "error")
        return redirect(url_for("note_detail", note_id=note_id))

    try:
        new_parent_id = int(new_parent_id)
    except ValueError:
        flash("Invalid parent ID", "error")
        return redirect(url_for("note_detail", note_id=note_id))

    try:
        noteapi.attach_note_to_parent(note_id, new_parent_id)
        flash("Note moved successfully", "success")
    except requests.exceptions.HTTPError as e:
        handle_http_error(e)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

    return redirect(url_for("note_detail", note_id=note_id))


def handle_http_error(error):
    if error.response.status_code == 404:
        flash("Note not found", "danger")
    else:
        flash(f"An error occurred: {error}", "danger")


@app.route("/upload_asset", methods=["GET", "POST"])
def upload_asset():
    if request.method == "POST":
        file = request.files.get("file")
        custom_filename = request.form.get("location")

        if file:
            if filename := file.filename:
                file_path = os.path.join("temp", filename)
                os.makedirs("temp", exist_ok=True)  # Ensure the temp directory exists
                file.save(file_path)

                try:
                    # If custom filename provided, use that as the upload path instead
                    upload_path = os.path.join(
                        "temp", custom_filename if custom_filename else filename
                    )
                    if custom_filename:
                        os.rename(file_path, upload_path)
                        file_to_cleanup = upload_path
                    else:
                        file_to_cleanup = file_path

                    result = assetsapi.upload_asset(
                        upload_path if custom_filename else file_path
                    )
                    flash(
                        f"File uploaded successfully. asset_id: {result.id}, server_filename: {result.location}\n",
                        "success",
                    )
                    flash(f"{result.get_markdown_link()}", "success")
                    # NOTE Don't return to original page, this is simpler
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}", "error")
                finally:
                    # Clean up the temporary file - either the renamed one or original
                    if os.path.exists(file_to_cleanup):
                        os.remove(file_to_cleanup)
            else:
                flash("Please provide a file. Unable to get a filename", "error")
        else:
            flash("Please provide a file.", "error")

    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("upload_asset.html", tree_html=tree_html)


@app.route("/assets")
def list_assets():
    assets = assetsapi.get_all_assets()
    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("asset_list.html", assets=assets, tree_html=tree_html)


@app.route("/delete_asset/<int:asset_id>")
def delete_asset(asset_id: int):
    try:
        assetsapi.delete_asset(asset_id)
        flash("Asset deleted successfully", "success")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            flash("Asset not found", "danger")
        else:
            flash(f"An error occurred: {e}", "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Request failed: {e}", "danger")

    return redirect(url_for("list_assets"))


@app.route("/edit_asset/<int:asset_id>")
def edit_asset(asset_id):
    # Placeholder for edit_asset route
    # This should be implemented later
    flash("Edit asset functionality is not yet implemented", "info")
    return redirect(url_for("list_assets"))


@app.route("/m/<string:maybe_id>", methods=["GET"])
def get_asset(maybe_id):
    """
    Retrieve an asset by filename and redirect to its download URL.

    Args:
        maybe_id (str): The asset ID or filename.

    Returns:
        Response: A redirection to the asset's download URL or a 404 error if not found.
    """
    # Construct the API URL
    api_url = f"{API_BASE_URL}/assets/download/{maybe_id}"

    # Convert Flask request headers to a dictionary
    headers = dict(request.headers)

    # Forward the GET request to the API URL
    try:
        # Use the transformed headers dictionary
        response = requests.get(api_url, headers=headers, timeout=5)

        # Create a new response with the data from the API
        forwarded_response = Response(
            response.content, response.status_code, dict(response.headers.items())
        )
        return forwarded_response

    except requests.exceptions.RequestException as e:
        # If there's an issue with connecting to the API, return a 502 Bad Gateway error
        return Response(str(e), status=502)


# NOTE The following will not work:
# return redirect(f"{API_BASE_URL}/assets/download/{maybe_id}")
# Ass the REST API may be running inside a container with a hostname not accessible to the user


@app.route("/manage_tags/<int:note_id>", methods=["GET", "POST"])
def manage_tags(note_id):
    note = noteapi.get_note(note_id)
    if request.method == "POST":
        # Get the list of selected tag IDs from the form
        selected_tag_ids = request.form.getlist("tags")
        selected_tag_ids = [int(tag_id) for tag_id in selected_tag_ids]

        # Get current tags to determine which to add/remove
        current_tags = get_note_tags(note_id)
        current_tag_ids = [tag.id for tag in current_tags]

        # Determine which tags to add and remove
        tags_to_add = [
            tag_id for tag_id in selected_tag_ids if tag_id not in current_tag_ids
        ]
        tags_to_remove = [
            tag_id for tag_id in current_tag_ids if tag_id not in selected_tag_ids
        ]

        try:
            # Remove tags that were unchecked
            for tag_id in tags_to_remove:
                tagapi.detach_tag_from_note(note_id, tag_id)

            # Add newly checked tags
            for tag_id in tags_to_add:
                tagapi.attach_tag_to_note(note_id, tag_id)

            flash("Tags updated successfully", "success")
        except requests.exceptions.RequestException as e:
            flash(f"Error updating tags: {str(e)}", "error")

        return redirect(url_for("note_detail", note_id=note_id))

    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree, note_id=note_id)
    tree_html = Markup(tree_html)

    # Get current tags for the note
    current_tags = get_note_tags(note_id)

    # Get all available tags
    all_tags = tagapi.get_all_tags()

    return render_template(
        "manage_tags.html",
        note=note,
        tree_html=tree_html,
        current_tags=current_tags,
        all_tags=all_tags,
    )


@app.route("/manage_all_tags")
def manage_all_tags():
    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    tags = tagapi.get_all_tags()
    return render_template("manage_all_tags.html", tags=tags, tree_html=tree_html)


@app.route("/create_tag", methods=["POST"])
def create_tag():
    name = request.form.get("name")
    if not name:
        flash("Tag name is required", "error")
        return redirect(url_for("manage_all_tags"))

    try:
        tagapi.create_tag(name)
        flash("Tag created successfully", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Error creating tag: {str(e)}", "error")

    return redirect(url_for("manage_all_tags"))


@app.route("/rename_tag/<int:tag_id>", methods=["POST"])
def rename_tag(tag_id):
    new_name = request.form.get("name")
    if not new_name:
        flash("Tag name is required", "error")
        return redirect(url_for("manage_all_tags"))

    try:
        tagapi.update_tag(tag_id, new_name)
        flash("Tag renamed successfully", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Error renaming tag: {str(e)}", "error")

    return redirect(url_for("manage_all_tags"))


@app.route("/delete_tag/<int:tag_id>", methods=["POST"])
def delete_tag(tag_id):
    try:
        tagapi.delete_tag(tag_id)
        flash("Tag deleted successfully", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Error deleting tag: {str(e)}", "error")

    return redirect(url_for("manage_all_tags"))


@app.route("/api/attach_child_tag", methods=["POST"])
def attach_child_tag_endpoint():
    data = request.get_json()
    parent_id = data.get("parent_tag_id")
    child_id = data.get("child_tag_id")

    if not parent_id or not child_id:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        tagapi.attach_tag_to_parent(child_id=child_id, parent_id=parent_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/detach_note_from_tag", methods=["POST"])
def detach_note_from_tag_endpoint():
    data = request.get_json()
    note_id = data.get("note_id")
    tag_id = data.get("tag_id")

    if not note_id or not tag_id:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        tagapi.detach_tag_from_note(note_id=note_id, tag_id=tag_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/attach_note_to_tag", methods=["POST"])
def attach_note_to_tag_endpoint():
    data = request.get_json()
    note_id = data.get("note_id")
    tag_id = data.get("tag_id")

    if not note_id or not tag_id:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        tagapi.attach_tag_to_note(note_id=note_id, tag_id=tag_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/attach_child_note", methods=["POST"])
def attach_child_note_endpoint():
    data = request.get_json()
    parent_id = data.get("parent_note_id")
    child_id = data.get("child_note_id")

    if not parent_id or not child_id:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        noteapi.attach_note_to_parent(child_note_id=child_id, parent_note_id=parent_id)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recent")
def recent_pages():
    recent_notes = get_recent_notes(limit=50)  # Adjust the limit as needed
    notes_tree = noteapi.get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    return render_template(
        "recent_pages.html",
        recent_notes=recent_notes,
        tree_html=tree_html,
    )


@app.context_processor
def inject_tags():
    return dict(tags=tagapi.get_tags_tree())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
