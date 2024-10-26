import re

# INLINE_MATH_PATTERN = re.compile(r"\$(.+?)\$")
# BLOCK_MATH_PATTERN = re.compile(r"\$\$([\s\S]+?)\$\$")

BLOCK_MATH_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
# TODO is Dotall needed here?
INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$((?!\$).+?)(?<!\$)\$", re.DOTALL)
