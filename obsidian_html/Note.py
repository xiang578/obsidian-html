import os
import regex as re
from obsidian_html.utils import slug_case, md_link, render_markdown
from obsidian_html.format import format_tags, format_blockrefs
from obsidian_html.Link import Link


class Note:
    def __init__(self, path, is_extra_dir = False):
        self.path = path
        self.filename = os.path.split(path)[-1]
        self.title = self.filename.replace(".md", "")
        self.filename_html = slug_case(self.title) + ".html"
        self.is_extra_dir = is_extra_dir
        self.link = Link(self.title)

        with open(path, encoding="utf8") as f:
            self.content = f.read()

        self.backlinks = ""

        self.links = self.links_in_file()

        self.convert_obsidian_syntax()
            
    def links_in_file(self):
        """Returns a list of all links in the note."""
        matches = re.finditer(r"\[{2}(.*?)\]{2}", self.content)

        links = []
        for match in matches:
            link = Link(match.group(1))
            links.append(link)

        return links
    
    def find_backlinks(self, others):
        """Returns a list of Link objects linking to all the notes in 'others' that reference self"""
        backlinks = []
        for other in others:
            if self == other:
                continue
            if self.link in other.links:
                backlinks.append(other.link)

        backlinks = sorted(backlinks, key=lambda link: link.file)

        return backlinks
    
    def convert_obsidian_syntax(self):
        """Converts Obsidian syntax into pure Markdown.
        Actually, that's a lie, features that aren't supported by John Gruber's Markdown is mostly
        converted into Pandoc's Markdown Flavour."""
        for link in self.links:
            self.content = self.content.replace(f"[[{link.obsidian_link}]]", link.md_link())
            
        self.content =  format_blockrefs(format_tags(self.content))
    
    def html(self, pandoc=False):
        """Returns the note formatted as HTML. Will use markdown2 as default, with the option of pandoc (WIP)"""
        document = self.content
        if pandoc:
            # Still WIP
            import pypandoc
            filters = ['pandoc-xnos']
            args = []
            html = pypandoc.convert_text(document, 'html', format='md', filters=filters, extra_args=args)
        else:
            html = render_markdown(document)

        # Wrapping converted markdown in a div for styling
        html = f"<div id=\"content\">{html}</div>"

        return html
    
    def __eq__(self, other):
        return self.path == other.path
            
