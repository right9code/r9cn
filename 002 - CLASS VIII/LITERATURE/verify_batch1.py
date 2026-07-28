import os

file1_path = "/home/right9zzz/Z/01 - VAULTS/PwD/002 - CLASS VIII/LITERATURE/C08 - 01 - THE WIT THAT WON HEARTS.md"
file2_path = "/home/right9zzz/Z/01 - VAULTS/PwD/002 - CLASS VIII/LITERATURE/C08 - 02 - A CONCRETE EXAMPLE - POETRY.md"
file3_path = "/home/right9zzz/Z/01 - VAULTS/PwD/002 - CLASS VIII/LITERATURE/C08 - 03 - WISDOM PAVES THE WAY.md"

files = [file1_path, file2_path, file3_path]

for filepath in files:
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    assert "\n\n---\n\n" in text, f"Missing \\n\\n---\\n\\n separator in {filename}"
    
    parts = text.split("\n\n---\n\n")
    answer_part = parts[-1]
    
    lines = answer_part.split('\n')
    
    # Check headers
    assert lines[0].startswith("# Answers – "), f"Missing main header in {filename}: {lines[0]}"
    
    # Check trailing spaces line by line
    errors = []
    for idx, line in enumerate(lines, 1):
        if line == "":
            continue
        elif line.startswith("#") or line == "---":
            if line.endswith(" "):
                errors.append(f"Line {idx} (Header/Separator) has trailing spaces: {repr(line)}")
        else:
            if not line.endswith("  "):
                errors.append(f"Line {idx} does NOT end with 2 spaces: {repr(line)}")
            elif line.endswith("   "):
                errors.append(f"Line {idx} has MORE than 2 trailing spaces: {repr(line)}")
    
    if errors:
        print(f"FAILED verification for {filename}:")
        for err in errors[:10]:
            print("  ", err)
    else:
        print(f"PASSED verification for {filename} ({len(lines)} lines in answer section)")

