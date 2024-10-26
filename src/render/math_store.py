from render.regex_patterns import INLINE_MATH_PATTERN, BLOCK_MATH_PATTERN


class MathStore:
    """
    A class that pulls math blocks from a markdown document, marks the region,
    and then restores the math blocks after the markdown has been converted to HTML.
    """

    def __init__(self):
        self.math_blocks = []
        self.BLOCK_MATH_PATTERN = BLOCK_MATH_PATTERN
        self.INLINE_MATH_PATTERN = INLINE_MATH_PATTERN

    def preserve_math(self, text: str) -> str:
        # Preserve math environments
        text = self.BLOCK_MATH_PATTERN.sub(self._preserve_math, text)
        text = self.INLINE_MATH_PATTERN.sub(self._preserve_math, text)
        return text

    def restore_math(self, text: str) -> str:
        # Restore math environments
        return self._restore_math(text)

    def _preserve_math(self, match):
        math = match.group(0)
        placeholder = f"MATH_PLACEHOLDER_{len(self.math_blocks)}"
        self.math_blocks.append(math)
        return placeholder

    def _restore_math(self, text):
        for i, math in enumerate(self.math_blocks):
            placeholder = f"MATH_PLACEHOLDER_{i}"
            text = text.replace(placeholder, math)
        return text
