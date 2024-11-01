#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash, current_app, abort
from markupsafe import Markup
import os
from src.api.assets.upload import upload_file
from src.api.assets.list import get_assets
from src.api.get.notes import (
    get_notes,
    get_note,
    get_notes_tree,
    build_notes_tree_html,
    find_note_path,
    search_notes,
    get_full_titles,
    get_recent_notes,
    get_note_backlinks,
    get_note_forward_links,
)
from src.api.put.notes import update_server_note
from src.api.post.notes import create_note
from src.api.assets.list import get_asset_id
from src.api.delete.notes import delete_note
from src.api.post.note_hierarchy import update_note_hierarchy
from src.render.render_markdown import Markdown
import requests


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key


@app.context_processor
def inject_all_notes():
    return dict(all_notes=get_notes())

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
    md_obj = Markdown(content)
    md = md_obj.make_html()
    note = get_note(1)

    return render_template(
        "note_detail.html", note=note, content=md, footer="Bar", tree_html=tree_html
    )


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    base_url = current_app.config['API_BASE_URL']
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
    base_url = current_app.config['API_BASE_URL']
    def get_backlinks_for_current_note():
        base_url = current_app.config['API_BASE_URL']
        if 'note_id' in request.view_args:
            note_id = request.view_args['note_id']
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
                url=current_app.config['API_BASE_URL'], title=title, content=content
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
        create_note(url=current_app.config['API_BASE_URL'], title=title, content=content)
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

@app.route('/upload_asset', methods=['GET', 'POST'])
def upload_asset():
    if request.method == 'POST':
        file = request.files.get('file')
        description = request.form.get('description')

        if file:
            if (filename := file.filename):
                filename = file.filename
                file_path = os.path.join('temp', filename)
                os.makedirs('temp', exist_ok=True)  # Ensure the temp directory exists
                file.save(file_path)

                try:
                    result = upload_file(file_path, base_url=current_app.config['API_BASE_URL'], description=description)
                    flash(f"File uploaded successfully. asset_id: {result.id}, server_filename: {result.filename} API: {result.message}", 'success')
                    # TODO maybe return to the original page?
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}", 'error')
                finally:
                    os.remove(file_path)  # Clean up the temporary file
            else:
                flash("Please provide a file. Unable to get a filename", 'error')
        else:
            flash("Please provide a file.", 'error')

    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template('upload_asset.html', tree_html=tree_html)


@app.route("/assets")
def list_assets():
    assets = get_assets(current_app.config['API_BASE_URL'])
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template("asset_list.html", assets=assets, tree_html=tree_html)

@app.route('/edit_asset/<int:asset_id>')
def edit_asset(asset_id):
    # Placeholder for edit_asset route
    # This should be implemented later
    flash("Edit asset functionality is not yet implemented", "info")
    return redirect(url_for('list_assets'))


@app.route('/m/<string:maybe_id>', methods=['GET'])
def get_asset(maybe_id):
    """
    Retrieve an asset by ID or filename and redirect to its download URL.

    Args:
        maybe_id (str): The asset ID or filename.

    Returns:
        Response: A redirection to the asset's download URL or a 404 error if not found.
    """

    # Assume that it's a filename, if nothing is matched, fallback to an ID
    # users should link to filenames, not IDs
    # Because the filenames can be modified by the user and this may fall out of sync
    # with the ID.
    # The API will likely be updated to make the filename the primary key
    api_url = current_app.config['API_BASE_URL']
    id = None

    # First, try resolving by filename
    id = get_asset_id(api_url, maybe_id)

    if id is None:
        # If filename resolution fails, fallback to resolving by ID
        if maybe_id.isdigit():
            id = int(maybe_id)
        else:
            # If maybe_id is neither a valid filename nor a numeric ID
            abort(404, description="Asset not found.")

    # Construct the download URL
    download_url = f"{api_url}/assets/{id}/download"

    print(f"{download_url=}")

    # Redirect to the download URL
    return redirect(download_url)


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

