import argparse
import json
import re
from pathlib import Path

STRING = r'"((?:[^"\\\n]|\\.)*)"'
MODULE = re.compile(r'super\(\s*[\w.]*Categories\.\w+\s*,\s*' + STRING + r'\s*,\s*' + STRING)
NAME = re.compile(r'\.name\(' + STRING + r'\)')
DESCRIPTION = re.compile(r'\.description\(' + STRING + r'\)')
GROUP = re.compile(r'createGroup\(' + STRING + r'\)')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("dictionary", type=Path)
    parser.add_argument("--output", type=Path, default=Path("untranslated.json"))
    return parser.parse_args()


def to_title(name):
    return " ".join(part[:1].upper() + part[1:] for part in name.split("-"))


def unescape(text):
    try:
        return json.loads('"' + text + '"')
    except json.JSONDecodeError:
        return text


def strings_in(source):
    found = set()
    for path in (source / "src/main/java").rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in MODULE.finditer(text):
            found.add(to_title(unescape(match.group(1))))
            found.add(unescape(match.group(2)))
        for match in NAME.finditer(text):
            found.add(to_title(unescape(match.group(1))))
        for pattern in (DESCRIPTION, GROUP):
            found.update(unescape(match.group(1)) for match in pattern.finditer(text))
    return found


def main():
    arguments = parse_arguments()
    translated = json.loads(arguments.dictionary.read_text(encoding="utf-8"))
    found = strings_in(arguments.source)
    untranslated = {text: "" for text in sorted(found) if not translated.get(text)}

    arguments.output.write_text(json.dumps(untranslated, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(found)} strings found, {len(untranslated)} untranslated -> {arguments.output}")


if __name__ == "__main__":
    main()
