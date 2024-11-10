#!/usr/bin/env python
import sys
import os

# TODO this should be interpreted from the CLI
# API_BASE_URL = "http://vidar:37240"
# Or possibly

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
from markupsafe import Markup
from typing import List, Optional, Dict
import os
import api

from src.api import note_create as create_note

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
    attach_note_to_parent,
    get_note_tag_relations,
    get_tag,
    get_note_without_content,
    Tag,
    NoteWithoutContent,
    get_tags_tree,
)
from src.api import get_all_assets as get_assets
from src.api import get_rendered_note
from src.api import upload_asset as upload_file
import requests

# BEGIN: API functions that should be implemented by server


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
            html = f'<li class="note-item" draggable="true" data-note-id="{note.id}"><details {status}><summary>{hyperlink}</summary>\n<ul>'

            for child in note.children:
                html += render_note(child, i + 1)
            html += "</ul>\n</details>\n</li>"
        else:
            html = f'<li class="note-item" draggable="true" data-note-id="{note.id}">{hyperlink}</li>'

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
    # return redirect(url_for("note_detail", note_id=1))
    # Redirect to recent pages
    return redirect(url_for("recent_pages"))


@app.route("/tags/<int:tag_id>")
def tag_detail(tag_id: int):
    notes = get_tag_notes(tag_id)
    tag = get_tag(tag_id)
    return render_template("tagged_pages_list.html", notes=notes, tag=tag)


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    base_url = api_base_url()
    note = get_note(note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    # Get backlinks for the current note
    backlinks = get_note_backlinks(note_id, base_url=base_url)
    forwardlinks = get_note_forward_links(note_id, base_url=base_url)

    # Get tags (TODO this needs an endpoint)

    note_tags = get_note_tag_relations()
    tags = [get_tag(nt.tag_id) for nt in note_tags if nt.note_id == note_id]

    # Parse the markdown content
    html_content = get_rendered_note(note_id, format="html")

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
    note_tags = get_note_tag_relations()
    tags = [get_tag(nt.tag_id) for nt in note_tags if nt.note_id == note_id]
    return tags


def get_tag_notes(tag_id) -> List[NoteWithoutContent]:
    note_tags = get_note_tag_relations()
    relevant_note_tags = [nt for nt in note_tags if nt.tag_id == tag_id]
    all_note_details = [
        get_note_without_content(nt.note_id) for nt in relevant_note_tags
    ]
    return all_note_details


@app.context_processor
def inject_backlinks():
    def get_backlinks_for_current_note():
        if "note_id" in request.view_args:
            note_id = request.view_args["note_id"]
            return get_note_backlinks(note_id, base_url=api_base_url())
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
    html_content = get_rendered_note(note_id, format="html")

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
        notes_tree = get_notes_tree()
        tree_html = build_notes_tree_html(notes_tree)
        tree_html = Markup(tree_html)

        return render_template("note_create.html", tree_html=tree_html, title="")
    elif request.method == "POST":
        content = request.form.get("content")
        title = request.form.get("title")
        try:
            response = create_note(
                base_url=api_base_url(), title=title or "", content=content or ""
            )

            if "error" in response:
                flash(f"Error creating note: {response['error']}", "error")
                return redirect(url_for("create_note_page"))

            id = response.get("id")
            if id:
                if parent_id:
                    try:
                        attach_note_to_parent(
                            child_note_id=id,
                            parent_note_id=parent_id,
                            base_url=api_base_url()
                        )
                    except requests.exceptions.RequestException as e:
                        flash(f"Note created but failed to attach to parent: {str(e)}", "warning")
                        return redirect(url_for("note_detail", note_id=id))
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
        _note = api.update_note(
            note_id,
            UpdateNoteRequest(title=title, content=content),
            base_url=api_base_url(),
        )
        # Refresh the page to show the updated note
    elif request.method == "PUT":
        create_note(base_url=api_base_url(), title=title or "", content=content or "")
        _note = api.update_note(
            note_id,
            UpdateNoteRequest(title=title, content=content),
            base_url=api_base_url(),
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
    search_results = search_notes(query)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    ids = [n.id for n in search_results]
    full_titles = get_full_titles(notes_tree)

    # TODO this should return the tree and construct the nested title
    # Maybe regail this to the server?
    search_results = []
    for note_id in ids:
        note = get_note(note_id)
        html_content = get_rendered_note(note.id, format="html")
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
        api.delete_note(note_id)
        flash("Note deleted successfully", "success")
        return redirect(url_for("root"))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            flash("Note not found", "danger")
        else:
            flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("note_detail", note_id=note_id))


@app.route("/note/<int:note_id>/detach", methods=["POST"])
def detach_note(note_id):
    try:
        api.detach_note_from_parent(note_id, base_url=api_base_url())
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
        attach_note_to_parent(note_id, new_parent_id, base_url=api_base_url())
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

                    result = upload_file(
                        upload_path if custom_filename else file_path,
                        base_url=api_base_url(),
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

    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("upload_asset.html", tree_html=tree_html)


@app.route("/assets")
def list_assets():
    assets = get_assets(api_base_url())
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("asset_list.html", assets=assets, tree_html=tree_html)


@app.route("/delete_asset/<int:asset_id>")
def delete_asset(asset_id: int):
    try:
        api.delete_asset(asset_id)
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

    Notes:
        Due to cross site scripting, ensure that the API_BASE_URL aligns with the server's URL.

        e.g. if the server is running on localhost:5000, the API_BASE_URL should be http://localhost:37240
             if the server is accessed at ds.myserver:5000 the API_BASEURL should be http://ds.api:37240
             if the server is accessed at ds.flask.myserver the API_BASEURL should be http://ds.api.myserver
    """
    return redirect(f"{api_base_url()}/assets/download/{maybe_id}")


@app.route("/manage_tags/<int:note_id>", methods=["GET", "POST"])
def manage_tags(note_id):
    note = get_note(note_id)
    if request.method == "POST":
        # Get the list of selected tag IDs from the form
        selected_tag_ids = request.form.getlist("tags")
        selected_tag_ids = [int(tag_id) for tag_id in selected_tag_ids]

        # Get current tags to determine which to add/remove
        current_tags = get_note_tags(note_id)
        current_tag_ids = [tag.id for tag in current_tags]

        # Determine which tags to add and remove
        tags_to_add = [tag_id for tag_id in selected_tag_ids if tag_id not in current_tag_ids]
        tags_to_remove = [tag_id for tag_id in current_tag_ids if tag_id not in selected_tag_ids]

        try:
            # Remove tags that were unchecked
            for tag_id in tags_to_remove:
                api.detach_tag_from_note(note_id, tag_id, base_url=api_base_url())

            # Add newly checked tags
            for tag_id in tags_to_add:
                api.attach_tag_to_note(note_id, tag_id, base_url=api_base_url())

            flash("Tags updated successfully", "success")
        except requests.exceptions.RequestException as e:
            flash(f"Error updating tags: {str(e)}", "error")

        return redirect(url_for("note_detail", note_id=note_id))

    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Get current tags for the note
    current_tags = get_note_tags(note_id)

    # Get all available tags
    all_tags = api.get_all_tags()

    return render_template(
        "manage_tags.html",
        note=note,
        tree_html=tree_html,
        current_tags=current_tags,
        all_tags=all_tags
    )

@app.route("/manage_all_tags")
def manage_all_tags():
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    tags = api.get_all_tags()
    return render_template("manage_all_tags.html", tags=tags, tree_html=tree_html)

@app.route("/create_tag", methods=["POST"])
def create_tag():
    name = request.form.get("name")
    if not name:
        flash("Tag name is required", "error")
        return redirect(url_for("manage_all_tags"))

    try:
        api.create_tag(name, base_url=api_base_url())
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
        api.update_tag(tag_id, new_name, base_url=api_base_url())
        flash("Tag renamed successfully", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Error renaming tag: {str(e)}", "error")

    return redirect(url_for("manage_all_tags"))

@app.route("/delete_tag/<int:tag_id>", methods=["POST"])
def delete_tag(tag_id):
    try:
        api.delete_tag(tag_id, base_url=api_base_url())
        flash("Tag deleted successfully", "success")
    except requests.exceptions.RequestException as e:
        flash(f"Error deleting tag: {str(e)}", "error")

    return redirect(url_for("manage_all_tags"))

@app.route("/api/attach_child_note", methods=["POST"])
def attach_child_note_endpoint():
    data = request.get_json()
    parent_id = data.get('parent_note_id')
    child_id = data.get('child_note_id')
    
    if not parent_id or not child_id:
        return jsonify({"error": "Missing required parameters"}), 400
        
    try:
        attach_note_to_parent(
            child_note_id=child_id,
            parent_note_id=parent_id,
            base_url=api_base_url()
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


@app.context_processor
def inject_tags():
    return dict(tags=api.get_tags_tree(base_url=api_base_url()))

def api_base_url():
    from config import Config

    return f"{Config.API_SCHEME}://{Config.API_HOST}:{Config.API_PORT}"


if __name__ == "__main__":
    api_host = os.getenv("DRAFTSMITH_FLASK_API_HOST", "vidar")
    api_port = os.getenv("DRAFTSMITH_FLASK_API_PORT", "37240")
    app.config["API_BASE_URL"] = f"http://{api_host}:{api_port}"
    app.run(debug=True, host="0.0.0.0")
