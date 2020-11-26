import regex as re
from obsidian_html.utils import slug_case, md_link


def format_tags(document, tags):
    """Obsidian style tags. Removes #-icon and adds a span tag."""
    for tag in tags:
        document = document.replace("#" + tag, "<span class=\"tag\">" + tag + "</span>")

    return document


def format_blockrefs(document):
    """Formats Obsidian block references into a span element that can be linked to"""
    regex = re.compile(r" \^(.+)$", re.MULTILINE)
    matches = regex.finditer(document)

    for match in matches:
        document = document.replace(match.group(), f"<span id=\"{match.group(1)}\"></span>")
        
    return document

def format_highlights(document):
    """Formats the '==highlight==' directly into HTML."""
    regex = re.compile(r"==(.*?)==")
    matches = regex.finditer(document)

    for match in matches:
        document = document.replace(match.group(), f"<mark class=\"highlight\">{match.group(1)}</mark>)")
        
    return document