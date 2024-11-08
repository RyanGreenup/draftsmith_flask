#!/usr/bin/env python
import sys
import os

# TODO this should be interpreted from the CLI
API_BASE_URL = "http://localhost:37240"
# Or possibly
# current_app.config["API_BASE_URL"]

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel, Field
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
    send_from_directory,
    make_response,
)
from markupsafe import Markup
from typing import List, Optional, Dict, Any
import os
from src.api_old.assets.upload import upload_file
from src.api_old.assets.list import get_assets

# from src.api_old.get.notes import (
#      get_notes,
#      get_note,
#      get_notes_tree,
#      build_notes_tree_html,
#      find_note_path,
#      search_notes,
#      get_full_titles,
#      get_recent_notes,
#      get_note_backlinks,
#      get_note_forward_links,
#  )
# from src.api_old.put.notes import update_server_note
# from src.api_old.post.notes import create_note
from src.api import note_create as create_note

# from src.api_old.assets.list import get_asset_id
# from src.api_old.delete.notes import delete_note
# from src.api_old.post.note_hierarchy import update_note_hierarchy
from src.render.render_markdown import Markdown

from src.api import (
    get_notes_tree,
    TreeNote,
    get_note,
    get_all_notes,
    Note,
    search_notes,
    UpdateNoteRequest,
    get_note_backlinks,
    get_note_forward_links,
    Asset,
    attach_note_to_parent,
)
from src.api import get_all_assets as get_assets
from src.api import delete_note as api_delete_note
from src.api import update_note as api_update_note
from src.api import get_rendered_note
from src.api import render_markdown
import requests

# BEGIN: API glue
# This is a temporary solution because the API changed


def update_note_hierarchy(
    parent_note_id: int,
    child_note_id: int,
    hierarchy_type: str,
    base_url: str = "http://localhost:37238",
) -> Dict[str, Any]:
    """Update the hierarchical relationship between notes.

    Args:
        parent_note_id: ID of the parent note
        child_note_id: ID of the child note
        hierarchy_type: Type of hierarchy relationship
        base_url: Base URL of the API

    Returns:
        Dict containing success status
    """
    attach_note_to_parent(child_note_id, parent_note_id, base_url)
    return {"message": "Hierarchy updated successfully"}


def delete_note(
    note_id: int, base_url: str = "http://localhost:37238"
) -> Dict[str, str]:
    response = api_delete_note(note_id)
    return response.model_dump()


class AssetModel(BaseModel):
    id: int
    file_name: str
    asset_type: str
    description: str
    created_at: datetime


def Asset_to_asset_model(asset: Asset):
    return AssetModel(
        id=asset.id,
        file_name=asset.location,
        asset_type="Legacy Field",
        description=asset.description or "",
        created_at=asset.created_at,
    )


def get_asset_id(base_url: str, filename: str) -> Optional[int]:
    assets = get_assets(base_url)
    for asset in assets:
        if asset.file_name == filename:
            return asset.id
    return None


def update_server_note(
    note_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    base_url: str = "http://localhost:37238",
) -> Dict[str, Any]:
    update_note_request = UpdateNoteRequest(title=title, content=content)
    note = api_update_note(note_id, update_note_request)
    note_dict = note.model_dump()
    return note_dict


# END

# BEGIN: API functions that should be implemented by server

from datetime import datetime


def get_recent_notes(limit: int = 10) -> List[Note]:
    notes = get_all_notes()
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


def get_notes(
    base_url: str = "http://localhost:37240", ids: List[int] | None = None
) -> List[Note]:
    notes = get_all_notes()
    # Filter notes by ID if specified
    if ids:
        notes = [note for note in notes if note.id in ids]
    return notes


# END: API functions that should be implemented by server

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a real secret key


def build_notes_tree_html(notes_tree: List[TreeNote], fold_level: int = 2) -> str:
    def render_note(note: TreeNote, i: int) -> str:
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
            html = f"<li>{hyperlink}</li>"

        return html

    # Sort the top-level notes
    notes_tree.sort(key=lambda x: x.title)

    html = '<ul class="menu bg-base-200 rounded-box w-56">'
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
    # Get all the notes
    all_notes = get_notes()
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)

    # Wrap the HTML in Markup to prevent escaping
    tree_html = Markup(tree_html)

    s = "\n".join([str(note.model_dump()) for note in all_notes])
    s = f"```json\n{s}\n```"
    content = f"# My Notes\n## All Notes in Corpus\n {s}"
    # md_obj = Markdown(content)
    # md = md_obj.make_html()
    md = render_markdown(content)
    note = get_note(1)

    return render_template(
        "note_detail.html", note=note, content=md, footer="Bar", tree_html=tree_html
    )


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    base_url = API_BASE_URL
    note = get_note(note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    # Get backlinks for the current note
    backlinks = get_note_backlinks(note_id, base_url=base_url)
    forwardlinks = get_note_forward_links(note_id, base_url=base_url)

    # Parse the markdown content
    md_obj = Markdown(note.content)
    html_content = md_obj.make_html()
    html_content = get_rendered_note(note_id, format="html")

    return render_template(
        "note_detail.html",
        note=note,
        note_html=html_content,
        tree_html=tree_html,
        note_path=note_path or [],
        backlinks=backlinks,
        forwardlinks=forwardlinks,
    )


@app.context_processor
def inject_backlinks():
    base_url = API_BASE_URL

    def get_backlinks_for_current_note():
        base_url =API_BASE_URL
        if "note_id" in request.view_args:
            note_id = request.view_args["note_id"]
            return get_note_backlinks(note_id, base_url=base_url)
        return []

    return dict(backlinks=get_backlinks_for_current_note())


@app.route("/edit/<int:note_id>")
def edit_note(note_id):
    note = get_note(note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)
    md_obj = Markdown(note.content)
    html_content = md_obj.make_html()

    return render_template(
        "note_edit.html",
        note=note,
        note_html=html_content,
        tree_html=tree_html,
        note_path=note_path or [],
    )


@app.route("/notes/create", methods=["GET", "POST"])
def create_note_page():
    if request.method == "GET":
        notes_tree = get_notes_tree()
        tree_html = build_notes_tree_html(notes_tree)
        tree_html = Markup(tree_html)

        return render_template("note_create.html", tree_html=tree_html, title="")
    elif request.method == "POST":
        content = request.form.get("content")
        title = request.form.get("title")
        try:
            response = create_note(
                base_url=API_BASE_URL, title=title or "", content=content or ""
            )

            if "error" in response:
                flash(f"Error creating note: {response['error']}", "error")
                return redirect(url_for("create_note_page"))

            id = response.get("id")
            if id:
                return redirect(url_for("note_detail", note_id=id))
            else:
                flash("Error creating note: No ID returned", "error")
                return redirect(url_for("create_note_page"))
        except requests.exceptions.RequestException as e:
            flash(f"Error creating note: {str(e)}", "error")
            return redirect(url_for("create_note_page"))


# TODO Implement title
@app.route("/edit/<int:note_id>", methods=["POST", "PUT"])
def update_note(note_id):
    title = request.form.get("title")
    content = request.form.get("content")
    if request.method == "POST":
        update_server_note(note_id, title=title, content=content)
        # Refresh the page to show the updated note
    elif request.method == "PUT":
        create_note(
            base_url=API_BASE_URL, title=title or "", content=content or ""
        )
        update_server_note(note_id, title=title, content=content)
        # Refresh the page to show the updated note
    return redirect(url_for("note_detail", note_id=note_id))


@app.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return redirect(url_for("root"))

    # TODO maybe API should include a field with and withot the full name to
    # Save multiple requests?
    search_results = search_notes(query)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    ids = [n.id for n in search_results]
    # TODO this should return the tree and construct the nested title
    # Maybe regail this to the server?
    notes = [get_note(i) for i in ids]
    full_titles = get_full_titles(notes_tree)
    # Render the content for display
    for note in notes:
        md_obj = Markdown(note.content)
        html_content = md_obj.make_html()
        note.content = html_content
        # use a div to protect certain things
        note.content = "<div>" + note.content[:200] + "</div> ..."
        note.title = full_titles[note.id]

    return render_template(
        "note_search.html",
        query=query,
        search_results=notes,
        tree_html=tree_html,
        note=None,
    )


@app.route("/note/<int:note_id>/delete", methods=["POST"])
def delete_note_page(note_id):
    try:
        response = delete_note(note_id)
        if response.get("message") == "Note deleted successfully":
            flash("Note deleted successfully", "success")
            return redirect(url_for("root"))
        else:
            flash("Failed to delete note", "error")
            return redirect(url_for("note_detail", note_id=note_id))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("note_detail", note_id=note_id))


@app.route("/note/<int:note_id>/move", methods=["GET", "POST"])
def move_note(note_id):
    if request.method == "GET":
        return render_template("move_note.html", note_id=note_id)
    elif request.method == "POST":
        new_parent_id = request.form.get("new_parent_id")
        try:
            new_parent_id = int(new_parent_id)
            result = update_note_hierarchy(new_parent_id, note_id, "subpage")
            flash("Note moved successfully", "success")
        except ValueError:
            flash("Invalid parent ID", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("note_detail", note_id=note_id))


@app.route("/upload_asset", methods=["GET", "POST"])
def upload_asset():
    if request.method == "POST":
        file = request.files.get("file")
        description = request.form.get("description")

        if file:
            if filename := file.filename:
                filename = file.filename
                file_path = os.path.join("temp", filename)
                os.makedirs("temp", exist_ok=True)  # Ensure the temp directory exists
                file.save(file_path)

                try:
                    result = upload_file(
                        file_path,
                        base_url=API_BASE_URL,
                        description=description,
                    )
                    flash(
                        f"File uploaded successfully. asset_id: {result.id}, server_filename: {result.filename} API: {result.message}",
                        "success",
                    )
                    # TODO maybe return to the original page?
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}", "error")
                finally:
                    os.remove(file_path)  # Clean up the temporary file
            else:
                flash("Please provide a file. Unable to get a filename", "error")
        else:
            flash("Please provide a file.", "error")

    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("upload_asset.html", tree_html=tree_html)


@app.route("/assets")
def list_assets():
    assets = get_assets(API_BASE_URL)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("asset_list.html", assets=assets, tree_html=tree_html)


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
    return redirect(f"{API_BASE_URL}/assets/download/{maybe_id}")

@app.route("/recent")
def recent_pages():
    recent_notes = get_recent_notes(limit=50)  # Adjust the limit as needed
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    return render_template(
        "recent_pages.html",
        recent_notes=recent_notes,
        tree_html=tree_html,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
