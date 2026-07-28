import sys

def format_answer_text(raw_answer):
    lines = raw_answer.split('\n')
    formatted_lines = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            formatted_lines.append('')
        elif stripped.startswith('#') or stripped == '---':
            formatted_lines.append(stripped)
        else:
            formatted_lines.append(stripped + '  ')
    return '\n'.join(formatted_lines)

# Test with a snippet
sample = """---

# Answers – Test Title

## Let us discuss

**I. Test heading**
1. First line answer.
2. Second line answer.

```
code block inside notice
```"""

res = format_answer_text(sample)
for idx, l in enumerate(res.split('\n'), 1):
    print(f"{idx}: {repr(l)}")
