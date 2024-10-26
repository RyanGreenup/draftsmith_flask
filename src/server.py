from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import Markup
import os
from api.assets.upload import upload_file
from api.get.notes import (
    get_notes,
    get_note,
    get_notes_tree,
    build_notes_tree_html,
    find_note_path,
    search_notes,
    get_full_titles,
)
from api.put.notes import update_server_note
from api.post.notes import create_note
from api.delete.notes import delete_note
from api.post.note_hierarchy import update_note_hierarchy
from render.render_markdown import Markdown


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
    note = get_note(note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    # Parse the markdown content
    md_obj = Markdown(note.content)
    html_content = md_obj.make_html()

    return render_template(
        "note_detail.html",
        note=note,
        note_html=html_content,
        tree_html=tree_html,
        note_path=note_path or [],
    )


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
        # TODO url should be configurable
        response = create_note(
            url="http://localhost:37238/notes", title=title, content=content
        )
        # TODO the API should return the ID of the new note
        id = response.get("id")
        if id:
            return redirect(url_for("note_detail", note_id=id))
        else:
            return redirect(url_for("root"))


# TODO Implement title
@app.route("/edit/<int:note_id>", methods=["POST", "PUT"])
def update_note(note_id):
    title = request.form.get("title")
    content = request.form.get("content")
    if request.method == "POST":
        update_server_note(note_id, title=title, content=content)
        # Refresh the page to show the updated note
    elif request.method == "PUT":
        create_note(url="http://localhost:37238/notes", title=title, content=content)
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

@app.route('/upload_asset', methods=['GET', 'POST'])
def upload_asset_page():
    if request.method == 'POST':
        file = request.files.get('file')
        note_id = request.form.get('note_id')
        description = request.form.get('description')
        
        if file and note_id:
            filename = file.filename
            file_path = os.path.join('temp', filename)
            os.makedirs('temp', exist_ok=True)  # Ensure the temp directory exists
            file.save(file_path)
            
            try:
                result = upload_file(file_path, int(note_id), description)
                flash(f"File uploaded successfully. {result.message}", 'success')
                return redirect(url_for('note_detail', note_id=note_id))
            except Exception as e:
                flash(f"Error uploading file: {str(e)}", 'error')
            finally:
                os.remove(file_path)  # Clean up the temporary file
        else:
            flash("Please provide both a file and a note ID.", 'error')
    
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)
    return render_template('upload_asset.html', tree_html=tree_html)
