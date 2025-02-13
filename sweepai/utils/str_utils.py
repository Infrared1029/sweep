from dataclasses import fields
import hashlib
import os
import re
import time


DEFAULT_BOT_SUFFIX = "\n\n*This is an automated message generated by [Sweep AI](https://sweep.dev).*"
BOT_SUFFIX = os.environ.get("BOT_SUFFIX", DEFAULT_BOT_SUFFIX).replace("\\n", "\n")

if BOT_SUFFIX != DEFAULT_BOT_SUFFIX:
    print(f"Using custom bot suffix: {BOT_SUFFIX}")

FASTER_MODEL_MESSAGE = """\
You ran out of the free tier GPT-4 tickets! Here are your options:
- You can get a free trial of Sweep Pro to get unlimited Sweep issues [here](https://buy.stripe.com/00g5npeT71H2gzCfZ8).
- You can run Sweep with your own Anthropic and OpenAI API keys [here](https://docs.sweep.dev/cli).
- You can book a chat with us set up Sweep Enterprise [here](https://calendly.com/d/2n5-3qf-9xy/user-interview).
"""

sep = "\n---\n"
bot_suffix_starring = ""
bot_suffix = f"""
{sep}
> [!TIP]
> To recreate the pull request, edit the issue title or description."""
discord_suffix = ""

stars_suffix = ""

collapsible_template = """
<details {opened}>
<summary>{summary}</summary>

{body}
</details>
"""

checkbox_template = "- [{check}] {filename}\n{instructions}\n"

num_of_snippets_to_query = 30
total_number_of_snippet_tokens = 15_000
num_full_files = 2


def ordinal(n):
    return str(n) + (
        "th" if 4 <= n <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )


def format_sandbox_success(success):
    return "✓" if success else "❌ (`Sandbox Failed`)"


def create_collapsible(summary: str, body: str, opened: bool = False):
    return collapsible_template.format(
        summary=summary, body=body, opened="open" if opened else ""
    )


def inline_code(text: str):
    return f"<code>{text}</code>" if text else ""


def code_block(text: str):
    return f"<pre>{text}</pre>" if text else ""


def blockquote(text: str):
    text = text.replace("\n•", "<br/>•")
    return f"<blockquote>{text}\n</blockquote>" if text else ""

def bold(text: str):
    return f"<b>{text}</b>" if text else ""


def create_checkbox(title: str, body: str, checked: bool = False):
    return checkbox_template.format(
        check="X" if checked else " ", filename=title, instructions=body
    )


def strip_sweep(text: str):
    return (
        re.sub(
            r"^[Ss]weep\s?(\([Ss]low\))?(\([Mm]ap\))?(\([Ff]ast\))?\s?:", "", text
        ).lstrip(),
        re.search(r"^[Ss]weep\s?\([Ss]low\)", text) is not None,
        re.search(r"^[Ss]weep\s?\([Mm]ap\)", text) is not None,
        re.search(r"^[Ss]weep\s?\([Ss]ubissues?\)", text) is not None,
        re.search(r"^[Ss]weep\s?\([Ss]andbox?\)", text) is not None,
        re.search(r"^[Ss]weep\s?\([Ff]ast\)", text) is not None,
        re.search(r"^[Ss]weep\s?\([Ll]int\)", text) is not None,
    )


def clean_logs(logs: str):
    cleaned_logs = re.sub(r"\x1b\[.*?[@-~]", "", logs.replace("```", "\`\`\`"))
    cleaned_logs = re.sub("\n{2,}", "\n", cleaned_logs)
    cleaned_logs = re.sub("\r{2,}", "\n", cleaned_logs)
    cleaned_logs = cleaned_logs.strip("\n")
    cleaned_logs = cleaned_logs or "(nothing was outputted)"
    return cleaned_logs


def extract_lines(text: str, start: int, end: int):
    lines = text.splitlines(keepends=True)
    return "\n".join(lines[max(0, start) : min(len(lines), end)])


def add_line_numbers(text: str, start: int = 0):
    lines = text.splitlines(keepends=True)
    return "".join(f"{start + i} | {line}" for i, line in enumerate(lines))


def to_branch_name(s, max_length=40):
    branch_name = s.strip().lower().replace(" ", "_")
    branch_name = re.sub(r"[^a-z0-9_]", "", branch_name)
    return branch_name[:max_length]


def get_hash():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]

# used for getting all indices of a substring match
def get_all_indices_of_substring(content: str, substring: str):
    start = 0
    indices = []
    while True:
        index = content.find(substring, start)
        if index == -1:  # No more occurrences found
            break
        indices.append(index)
        start = index + 1  # Move past the last found occurrence
    return indices

# converts a single arbitrary object to xml string format
def object_to_xml(object: object, object_name: str):
    object_fields = [f"<{field.name}>\n{getattr(object, field.name)}\n</{field.name}>" for field in fields(object)]
    fields_strings = "\n".join(object_fields)
    object_string = f"<{object_name}>\n{fields_strings}\n</{object_name}>"
    return object_string

# converts a list of objects to xml string format
def objects_to_xml(objects: list[object], object_name: str, outer_field_name: str = ""):
    objects_string = ""
    for object in objects:
        objects_string += f"{object_to_xml(object, object_name)}\n"
    if outer_field_name:
        objects_string = f"<{outer_field_name}>\n{objects_string}</{outer_field_name}>"
    else:
        objects_string = f"<{object_name}s>\n{objects_string}</{object_name}s>"
    return objects_string

def extract_xml_tag(string: str, tag: str, include_closing_tag: bool = True):
    pattern = f"<{tag}>(.*?)</{tag}>" if include_closing_tag else f"<{tag}>(.*?)(\Z|</{tag}>)"
    match_ = re.search(pattern, string, re.DOTALL)
    if match_ is None:
        return None
    return match_.group(1).strip("\n")
