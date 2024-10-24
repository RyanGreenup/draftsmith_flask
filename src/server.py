from flask import Flask, render_template
from markupsafe import Markup
import markdown
from api.get.notes import (
    get_notes,
    get_note,
    get_notes_tree,
    build_notes_tree_html,
    find_note_path,
)
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
    note = get_note(all_notes, 1)

    return render_template(
        "note_detail.html", note=note, content=md, footer="Bar", tree_html=tree_html
    )


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    all_notes = get_notes()
    note = get_note(all_notes, note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    return render_template(
        "note_detail.html", note=note, tree_html=tree_html, note_path=note_path or []
    )


@app.route("/edit/<int:note_id>")
def edit_note(note_id):
    all_notes = get_notes()
    note = get_note(all_notes, note_id)
    notes_tree = get_notes_tree()
    tree_html = build_notes_tree_html(notes_tree)
    tree_html = Markup(tree_html)

    # Find the path to the current note
    note_path = find_note_path(notes_tree, note_id)

    return render_template(
        "note_edit.html", note=note, tree_html=tree_html, note_path=note_path or []
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
