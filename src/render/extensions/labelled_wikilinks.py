import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
import re
from flask import abort
from api_old.get.notes import get_note


class NoteLinkInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        try:
            # Extract the Components
            parts = m.group(1).split("|")
            note_id = int(parts[0])
            label = parts[1] if len(parts) > 1 else None

            # Get the note and extract the attributes
            note = get_note(note_id)
            title = note.title

            # Set the label and URL
            label = label if label else title if title else f"# {note_id}"
            url = f"{note_id}"  # note.title.replace(' ', '-').lower()  # Placeholder URL logic

            # Build the link element
            link = etree.Element("a", href=url)
            link.text = label
            return link, m.start(0), m.end(0)

        except Exception as e:
            # Handle note not found or any other errors
            error_elem = etree.Element("span")
            error_elem.text = f"[Error: Note {note_id} not found]"
            return error_elem, m.start(0), m.end(0)


class NoteLinkExtension(Extension):
    def extendMarkdown(self, md):
        # Regular expression for matching the custom syntax [[ID]] or [[ID|label]]
        # It should match either [[number]] or [[number|text]]
        NOTE_LINK_RE = r"\[\[(\d+(?:\|[^]]+)?)\]\]"
        md.inlinePatterns.register(
            NoteLinkInlineProcessor(NOTE_LINK_RE, md), "note_link", 175
        )


def make_extension(**kwargs):
    return NoteLinkExtension(**kwargs)
