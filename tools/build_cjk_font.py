import argparse
import json
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SOURCE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf"
REGULAR_WEIGHT = 400
PUNCTUATION_RANGES = (range(0x3000, 0x3040), range(0xFF01, 0xFF5F))
SYMBOLS = "…—–·•×÷°±≤≥≈←→↑↓"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("dictionary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, default=Path("NotoSansTC-variable.ttf"))
    parser.add_argument("--extra", type=Path, nargs="*", default=[])
    parser.add_argument("--big5", action="store_true")
    return parser.parse_args()


def non_ascii(text):
    return {char for char in text if ord(char) > 0x7F}


def big5_level_one():
    characters = set()
    for lead in range(0xA4, 0xC7):
        for trail in list(range(0x40, 0x7F)) + list(range(0xA1, 0xFF)):
            if lead == 0xC6 and trail > 0x7E:
                continue
            try:
                char = bytes([lead, trail]).decode("big5")
            except UnicodeDecodeError:
                continue
            if "\u4e00" <= char <= "\u9fff":
                characters.add(char)
    return characters


def collect_characters(arguments):
    dictionary = json.loads(arguments.dictionary.read_text(encoding="utf-8"))
    characters = set()
    for value in dictionary.values():
        characters |= non_ascii(value)
    for path in arguments.extra:
        characters |= non_ascii(path.read_text(encoding="utf-8"))
    for char_range in PUNCTUATION_RANGES:
        characters.update(chr(code) for code in char_range)
    characters.update(SYMBOLS)
    if arguments.big5:
        characters |= big5_level_one()
    return characters


def load_static_font(source):
    if not source.exists():
        urllib.request.urlretrieve(SOURCE_URL, source)
    return instancer.instantiateVariableFont(TTFont(source), {"wght": REGULAR_WEIGHT})


def subset_font(font, characters):
    options = subset.Options()
    options.layout_features = []
    options.hinting = False
    options.notdef_outline = True
    options.glyph_names = False
    options.name_IDs = [1, 2, 3, 4, 6]

    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=[ord(char) for char in characters] + list(range(0x20, 0x7F)))
    subsetter.subset(font)


def main():
    arguments = parse_arguments()
    characters = collect_characters(arguments)

    font = load_static_font(arguments.source)
    subset_font(font, characters)
    font.save(arguments.output)

    covered = set(font.getBestCmap())
    missing = sorted(char for char in characters if ord(char) not in covered)
    print(f"{arguments.output}: {len(characters)} characters, {arguments.output.stat().st_size // 1024} KB")
    if missing:
        print("missing glyphs: " + "".join(missing))


if __name__ == "__main__":
    main()
