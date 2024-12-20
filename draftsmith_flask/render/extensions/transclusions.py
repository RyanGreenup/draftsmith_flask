import os
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
from re import Pattern
from api_old.get.notes import get_notes, get_note
from render.math_store import MathStore
from render.regex_patterns import TRANSCLUSION_PATTERN

MAX_DEPTH = 10


class IncludeFilePreprocessor(Preprocessor):
    TRANSCLUSION_PATTERN = TRANSCLUSION_PATTERN

    def __init__(self, md, max_depth: int, inject_daisy_card_css: bool = True):
        super().__init__(md)
        self.max_depth = max_depth
        self.math_store = MathStore()
        self.inject_daisy_card_css = inject_daisy_card_css

    def wrap_with_css(self, title: str, content: str) -> str:
        return f"""
<div class="card bg-base-100 w-xl shadow-xl">
  <div class="card-body">
    <b class="card-title">{title}</b>
    <p>
      {content}
    </p>
  </div>
</div>"""

    def run(self, lines, depth=0):
        if depth >= self.max_depth:
            return lines  # Return the original lines if max depth is reached

        new_lines = []
        code_block = False
        code_span_pattern = re.compile(r"(`+)(.*?)\1")  # Match inline code spans

        for line in lines:
            # Detect code blocks (fenced with triple backticks)
            if line.strip().startswith("```"):
                code_block = not code_block
                new_lines.append(line)
                continue

            # Skip processing if we're in a code block
            if code_block:
                new_lines.append(line)
                continue

            # Process inline code spans and protect them
            protected_line = line
            inline_code_matches = list(code_span_pattern.finditer(line))
            for match in inline_code_matches:
                protected_segment = match.group(0)  # Full match with backticks
                # Temporarily replace inline code with a placeholder
                protected_line = protected_line.replace(
                    protected_segment, f"<<CODE{len(match.group(1))}>>"
                )

            # Find transclusion links in the line
            m = self.TRANSCLUSION_PATTERN.search(protected_line)
            if m:
                id = m.group(1)
                if id.isdigit():
                    try:
                        note = get_note(int(id))
                        file_content = note.content

                        # Preserve math in the file content
                        preserved_content = self.math_store.preserve_math(file_content)

                        # Create a new Markdown instance and parse the included file's content
                        included_md = markdown.Markdown(
                            extensions=self.md.registeredExtensions
                        )

                        # Increase the depth for this recursion level
                        included_preprocessor = IncludeFilePreprocessor(
                            included_md, self.max_depth
                        )
                        included_lines = included_preprocessor.run(
                            preserved_content.splitlines(), depth + 1
                        )

                        # Convert and restore math environments
                        included_html = included_md.convert("\n".join(included_lines))
                        restored_html = self.math_store.restore_math(included_html)

                        if self.inject_daisy_card_css:
                            restored_html = self.wrap_with_css(
                                f"<a href='/note/{id}'>↱ #{id}</a><span class='text-sm text-gray-500'> | <a href='/edit/{id}'>Edit</a></span>",
                                restored_html,
                            )

                        # Add the parsed HTML to new_lines
                        new_lines.append(restored_html)
                    except Exception as e:
                        new_lines.append(f"**Error:** Unable to find ID #`{id}`.")
                        new_lines.append(f"**Error:** {e}")
                else:
                    new_lines.append(
                        f"**Error:** Unable to extract ID from `{m.group(0)}`."
                    )
            else:
                # Restore inline code placeholders with their original content
                restored_line = protected_line
                for match in inline_code_matches:
                    restored_segment = match.group(0)
                    restored_line = restored_line.replace(
                        f"<<CODE{len(match.group(1))}>>", restored_segment
                    )
                new_lines.append(restored_line)

        return new_lines


class IncludeTransclusions(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            IncludeFilePreprocessor(md, max_depth=MAX_DEPTH), "include_file", 25
        )


def test_regex(reg_pattern: Pattern[str]):
    test_strings = [
        "![[Link]]",
        "![[Link|Text]]",
        "![[Link|Text|More text]]",
        "![[Link|Text|More text|Even more text]]",
    ]

    for string in test_strings:
        match = reg_pattern.search(string)
        if match:
            assert match.group(1) == "Link", "Failed to capture the link"


def makeExtension(**kwargs):
    return IncludeTransclusions(**kwargs)


# Usage Example:
if __name__ == "__main__":
    md_text = """
    This is a markdown example.

    ![[42]]

    More text here.
    """

    md = markdown.Markdown(extensions=["tables", IncludeTransclusions()])
    html = md.convert(md_text)
    print(html)
