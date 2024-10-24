from flask import Flask, render_template
from markupsafe import Markup
import markdown
from api.notes import (
    get_notes,
    get_note,
    get_notes_tree,
    build_notes_tree_html,
    find_note_path,
)


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
        "note_detail.html", note=note, tree_html=tree_html, note_path=note_path
    )


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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
