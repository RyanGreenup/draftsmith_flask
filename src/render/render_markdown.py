import markdown
# from markdown_extension_transclusion import IncludeFileExtension
# from markdown_extension_image_size_and_caption import ImageWithFigureExtension
from pygments.formatters import HtmlFormatter
from pathlib import Path
from render.extensions.transclusions import IncludeTransclusions
from render.math_store import MathStore
from render.extensions.labelled_wikilinks import NoteLinkExtension
from render.postprocess import fix_image_video_tags

# from regex_patterns import INLINE_MATH_PATTERN, BLOCK_MATH_PATTERN



def make_html(text: str) -> str:
    html_body = markdown.markdown(
        text,
        extensions=[
            IncludeTransclusions(),
            NoteLinkExtension(),
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
            IncludeTransclusions(),
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


class Markdown:
    def __init__(
        self, text: str, css_path: Path | None = None, dark_mode: bool = False
    ):
        self.css_path = css_path
        self.dark_mode = dark_mode
        self.text = text
        self.math_store = MathStore()


    def make_html(self) -> str:
        # Preserve math environments
        text = self.math_store.preserve_math(self.text)

        # Generate the markdown with extensions
        html_body = markdown.markdown(
            text,
            extensions=[
                IncludeTransclusions(),
                NoteLinkExtension(),
                "attr_list",
                # ImageWithFigureExtension(),
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

        # Restore math environments
        html_body = self.math_store.restore_math(html_body)

        # Postprocess the HTML
        html_body = fix_image_video_tags(html_body)

        return html_body

    def build_css(self) -> str:
        css_styles = ""
        # TODO CSS should be a class that reads the CSS once and caches it
        # Use @property to make it a read-only attribute with a setter and getter
        if self.css_path:
            # Glob the css_path
            if self.css_path.is_dir():
                css_files = self.css_path.glob("*.css")
                for css_file in css_files:
                    with open(css_file, "r") as file:
                        css_styles += file.read()
        # Add Pygments CSS for code highlighting
        formatter = HtmlFormatter(style="default" if not self.dark_mode else "monokai")
        pygments_css = formatter.get_style_defs(".highlight")

        # Modify Pygments CSS for dark mode
        if self.dark_mode:
            pygments_css = pygments_css.replace(
                "background: #f8f8f8", "background: #2d2d2d"
            )
            pygments_css += """
            .highlight {
                background-color: #2d2d2d;
            }
            .highlight pre {
                background-color: #2d2d2d;
            }
            .highlight .hll {
                background-color: #2d2d2d;
            }
            """

        css_styles += pygments_css

        # Add dark mode styles if enabled
        if self.dark_mode:
            dark_mode_styles = """
            body {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            a {
                color: #3794ff;
            }
            code {
                background-color: #2d2d2d;
            }
            .katex { color: #d4d4d4; }
            """
            css_styles += dark_mode_styles
        return css_styles

    def build_html(self, content_editable=False, local_katex=True) -> str:
        html_body = self.make_html()
        css_styles = self.build_css()
        content_editable_attr = 'contenteditable="true"' if content_editable else ""

        katex_dark_mode_styles = (
            """
        .katex { color: #d4d4d4; }
        """
            if self.dark_mode
            else ""
        )

        katex_min_css, katex_min_js, auto_render_min_js = get_katex_html(
            local=local_katex
        )

        # Allow separate dark mode styles
        if self.dark_mode:
            html_body = f'<div class="dark-mode">{html_body}</div>'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {katex_min_css}
            <style>
            {css_styles}
            {katex_dark_mode_styles}
            </style>
        </head>
        <body {content_editable_attr}>
            {html_body}
            {katex_min_js}
            {auto_render_min_js}
            <script>
            document.addEventListener("DOMContentLoaded", function() {{
                renderMathInElement(document.body, {{
                    delimiters: [
                      {{left: "$$", right: "$$", display: true}},
                      {{left: "$", right: "$", display: false}}
                    ]
                }});
            }});
            </script>
        </body>
        </html>
        """

        return html
