import os
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
from re import Pattern
from api.get.notes import get_notes, get_note
from render.math_store import MathStore

MAX_DEPTH = 10

class IncludeFilePreprocessor(Preprocessor):
    INCLUDE_RE = re.compile(r'!\[\[([^\]]+)\]\]')

    def __init__(self, md, max_depth: int):
        super().__init__(md)
        self.max_depth = max_depth
        self.math_store = MathStore()

    def run(self, lines, depth=0):
        if depth >= self.max_depth:
            return lines  # Return the original lines if max depth is reached

        new_lines = []
        for line in lines:
            m = self.INCLUDE_RE.search(line)
            if m:
                id = m.group(1)
                if id.isdigit():
                    try:
                        note = get_note(int(id))
                        file_content = f"[↱ #{id}](/note/{id})\n" + note.content

                        # Preserve math in the file content
                        preserved_content = self.math_store.preserve_math(file_content)

                        # Create a new Markdown instance and parse the included file's content
                        included_md = markdown.Markdown(extensions=self.md.registeredExtensions)

                        # Increase the depth for this recursion level
                        included_preprocessor = IncludeFilePreprocessor(included_md, self.max_depth)
                        included_lines = included_preprocessor.run(preserved_content.splitlines(), depth + 1)

                        # Convert and restore math environments
                        included_html = included_md.convert("\n".join(included_lines))
                        restored_html = self.math_store.restore_math(included_html)

                        # Add the parsed HTML to new_lines
                        new_lines.append(restored_html)
                    except Exception as e:
                        new_lines.append(f'**Error:** Unable to find ID #`{id}`.')
                        new_lines.append(f'**Error:** {e}')
                else:
                    new_lines.append(f'**Error:** Unable to extract ID from `{m.group(0)}`.')
            else:
                new_lines.append(line)
        return new_lines

class IncludeTransclusions(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            IncludeFilePreprocessor(md, max_depth=MAX_DEPTH),
            'include_file',
            25
        )

def test_regex(reg_pattern: Pattern[str]):
    test_strings = [
        '![[Link]]',
        '![[Link|Text]]',
        '![[Link|Text|More text]]',
        '![[Link|Text|More text|Even more text]]'
    ]

    for string in test_strings:
        match = reg_pattern.search(string)
        if match:
            assert match.group(1) == 'Link', "Failed to capture the link"

def makeExtension(**kwargs):
    return IncludeTransclusions(**kwargs)

# Usage Example:
if __name__ == '__main__':
    md_text = """
    This is a markdown example.

    ![[42]]

    More text here.
    """

    md = markdown.Markdown(extensions=[
        'tables', IncludeTransclusions()
    ])
    html = md.convert(md_text)
    print(html)

