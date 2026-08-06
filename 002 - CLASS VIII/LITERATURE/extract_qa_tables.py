"""
Extract answers from Literature chapters and generate Q&A tables.

For each chapter, this script:
1. Finds the existing "# Answers – Chapter name" section
2. Extracts both questions and answers from the entire document
3. Creates a combined Q&A table with Question + Answer columns
4. Writes the table to a new file: "C08 - XX - CHAPTER_NAME - QA TABLE.md"
"""

import os
import re
import glob

LIT_DIR = "/home/right9zzz/Z/01 - VAULTS/r9cn/002 - CLASS VIII/LITERATURE"

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_questions(content):
    """
    Extract all questions from the content.
    Questions appear as:
    - Numbered items: "1. What is..."
    - Sub-items: "(i) Identify..." "(ii) What does..."
    - Multiple choice: "- A. ..." "- B. ..."
    """
    questions = []
    lines = content.split('\n')
    current_heading = ""

    for line in lines:
        stripped = line.strip()

        # Track current section heading
        if stripped.startswith('#### ') or stripped.startswith('## '):
            current_heading = stripped
        elif stripped.startswith('**') and re.match(r'\*\*[IV]+\.\s', stripped):
            current_heading = stripped

        # Numbered question: "1. What does..."
        num_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if num_match and not stripped.startswith('*'):
            # Skip if it's already part of a table row
            if '|' in line and stripped.startswith('1.'):
                # Could be table content, check context
                pass
            else:
                questions.append((current_heading, num_match.group(2)))
                continue

        # Sub-item: "(i) ..." "(ii) ..."
        sub_match = re.match(r'^\((\w+)\)\s+(.+)', stripped)
        if sub_match:
            questions.append((current_heading, sub_match.group(2)))
            continue

    return questions

def get_answers_from_section(content):
    """
    Extract all answers from the "# Answers – Chapter name" section.
    """
    answers_idx = content.find("# Answers –")
    if answers_idx == -1:
        return []

    answers_text = content[answers_idx:]
    answers = []
    lines = answers_text.split('\n')
    current_heading = ""

    for line in lines:
        stripped = line.strip()

        # Track current section heading
        if stripped.startswith('#### ') or stripped.startswith('## '):
            current_heading = stripped
        elif stripped.startswith('**') and re.match(r'\*\*[IV]+\.\s', stripped):
            current_heading = stripped

        # Numbered answer
        num_match = re.match(r'^(\d+)[\.\)]\s+(.+)', stripped)
        if num_match:
            answers.append((current_heading, num_match.group(2)))
            continue

        # Sub-item answer
        sub_match = re.match(r'^\((\w+)\)\s+(.+)', stripped)
        if sub_match:
            answers.append((current_heading, sub_match.group(2)))
            continue

    return answers

def generate_qa_table(chapter_name, qa_pairs):
    """
    Generate a markdown table from Q&A pairs.
    """
    if not qa_pairs:
        return None

    lines = []
    lines.append(f"## Q&A Table – {chapter_name}")
    lines.append("")
    lines.append("| # | Question | Answer |")
    lines.append("|---|----------|--------|")

    for i, (q, a) in enumerate(qa_pairs, 1):
        # Clean markdown formatting for table display
        clean_q = re.sub(r'\*\*', '', q).strip()
        clean_a = re.sub(r'\*\*', '', a).strip()

        # Escape pipe characters
        clean_q = clean_q.replace('|', '\\|')
        clean_a = clean_a.replace('|', '\\|')

        # Limit line length for readability
        if len(clean_q) > 200:
            clean_q = clean_q[:200] + "..."
        if len(clean_a) > 200:
            clean_a = clean_a[:200] + "..."

        lines.append(f"| {i} | {clean_q} | {clean_a} |")

    return '\n'.join(lines)

def pair_questions_with_answers(questions, answers):
    """
    Pair questions with their corresponding answers by index.
    This works because the answers appear in the same order as questions.
    """
    pairs = []
    min_len = min(len(questions), len(answers))

    for i in range(min_len):
        pairs.append((questions[i][1], answers[i][1]))

    return pairs

def main():
    pattern = os.path.join(LIT_DIR, "C08 - *.md")
    files = sorted(glob.glob(pattern))

    print(f"Processing {len(files)} chapter files...\n")

    for filepath in files:
        filename = os.path.basename(filepath)
        chapter_name = filename.replace('.md', '').replace('C08 - ', '')

        try:
            content = read_file(filepath)

            # Get questions from main body (before Answers section)
            answers_idx = content.find("# Answers –")
            if answers_idx == -1:
                print(f"  SKIP: {filename} — no answers section")
                continue

            main_body = content[:answers_idx]

            # Get questions from main body and answers from answers section
            questions = get_questions(main_body)
            answers = get_answers_from_section(content)

            # Pair them up
            qa_pairs = pair_questions_with_answers(questions, answers)

            if not qa_pairs:
                print(f"  SKIP: {filename} — no Q&A pairs found (Q:{len(questions)} A:{len(answers)})")
                continue

            # Generate the table
            table = generate_qa_table(chapter_name, qa_pairs)

            if not table:
                print(f"  SKIP: {filename} — table generation failed")
                continue

            # Write to new file
            output_name = filename.replace('.md', ' - QA TABLE.md')
            output_path = os.path.join(LIT_DIR, output_name)
            write_file(output_path, table + '\n')

            print(f"  OK: {filename}")
            print(f"      -> {output_name}")
            print(f"      Q:{len(questions)} A:{len(answers)} Pairs:{len(qa_pairs)}\n")

        except Exception as e:
            print(f"  ERROR: {filename} — {e}\n")

if __name__ == "__main__":
    main()
