from flask import Flask, render_template, request, redirect, url_for
from markupsafe import Markup
from api.get.notes import (
    get_notes,
    get_note,
    get_notes_tree,
    build_notes_tree_html,
    find_note_path,
    search_notes,
    get_full_titles
)
from api.put.notes import update_server_note
from render.render_markdown import make_html



app = Flask(__name__)


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
    md = make_html(content)
    note = get_note(1)

    return render_template(
        "note_detail.html", note=note, content=md, footer="Bar", tree_html=tree_html
    )


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    all_notes = get_notes()
    note = get_note(note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    # Parse the markdown content
    note.content = make_html(note.content)

    return render_template(
        "note_detail.html", note=note, note_html=make_html(note.content), tree_html=tree_html, note_path=note_path or []
    )


@app.route("/edit/<int:note_id>")
def edit_note(note_id):
    all_notes = get_notes()
    note = get_note(note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    return render_template(
        "note_edit.html", note=note, note_html=make_html(note.content), tree_html=tree_html, note_path=note_path or []
    )


# TODO Implement title
@app.route("/edit/<int:note_id>", methods=["POST"])
def update_note(note_id):
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')

        # Here you would add logic to update the note with the provided id, title, and content.
        # TODO

        update_server_note(note_id, title=title, content=content)
        # Refresh the page to show the updated note
        return redirect(url_for("note_detail", note_id=note_id))



@app.route("/search")
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('root'))

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
        note.content = make_html(note.content)
        # use a div to protect certain things
        note.content = "<div>" + note.content[:200] + "</div> ..."
        note.title = full_titles[note.id]


    return render_template(
        "note_search.html",
        query=query,
        search_results=notes,
        tree_html=tree_html,
        note=None
    )




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
