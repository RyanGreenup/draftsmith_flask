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

