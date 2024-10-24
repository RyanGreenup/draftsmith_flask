from flask import Flask
from flask import render_template
import os
import markdown
from api.notes import get_notes, get_note


app = Flask(__name__)


@app.route("/")
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
    return render_template("base.html", content=md, footer="Bar", all_notes=all_notes)


@app.route("/note/<int:note_id>")
def note_detail(note_id):
    all_notes = get_notes()
    note = get_note(all_notes, note_id)

    return render_template("note_detail.html", note=note, all_notes=all_notes)


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
