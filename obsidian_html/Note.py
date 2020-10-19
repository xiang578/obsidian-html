import os
import regex as re
from obsidian_html.utils import slug_case, md_link
from obsidian_html.format import *


class Note:
    def __init__(self, path, is_extra_dir = False):
        self.path = path
        self.filename = os.path.split(path)[-1]
        self.filename_no_ext = self.filename.replace(".md", "")
        self.filename_html = slug_case(self.filename_no_ext) + ".html"
        self.is_extra_dir = is_extra_dir
        self.link = Link(self.filename_no_ext)
        with open(path, encoding="utf8") as f:
            self.content = f.read()
            
        self.links = self.links_in_file()
            
    def links_in_file(self):
        """Returns a list of all links in the note."""
        matches = re.finditer(r"\[{2}([^\]]*?)[|#\]]([^\]]*?)\]+", self.content)

        links = []
        for match in matches:
            link = Link(match.group(1), alias=match.group(2))
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

        backlinks = sorted(backlinks, key=lambda x: x.target)

        return backlinks
    
    def html(self, pandoc=False):
        # Formatting of Obsidian tags and links.
        # (I know, very Lisp-esque, but Python doesn't always need to be imperative :wink:)
        document = format_tags(
            format_internal_header_links(
                format_internal_aliased_links(
                    format_internal_links(
                        self.content))))

        if pandoc:
            # Still WIP
            import pypandoc
            filters = ['pandoc-xnos']
            args = []
            html = pypandoc.convert_text(document, 'html', format='md', filters=filters, extra_args=args)
        else:
            import markdown2
            # Escaped curly braces lose their escapes when formatted. I'm suspecting
            # this is from markdown2, as I haven't found anyplace which could
            # do this among my own formatter functions. Therefore I double escape them.
            document = document.replace(r"\{", r"\\{").replace(r"\}", r"\\}")

            markdown2_extras = [
                # Parser should work withouth strict linebreaks.
                "break-on-newline",
                # Support of ```-codeblocks and syntax highlighting.
                "fenced-code-blocks",
                # Make slug IDs for each header. Needed for internal header links.
                "header-ids",
                # Support for strikethrough formatting.
                "strike",
                # GFM tables.
                "tables",
                # Support for lists that start without a newline directly above.
                "cuddled-lists",
                # Have to support Markdown inside html tags
                "markdown-in-html",
                # Disable formatting via the _ character. Necessary for code an TeX
                "code-friendly",
                # Support for Obsidian's footnote syntax
                "footnotes"
            ]

            html = markdown2.markdown(document, extras=markdown2_extras)

        # Wrapping converted markdown in a div for styling
        html = f"<div id=\"content\">{html}</div>"

        return html
    
    def __eq__(self, other):
        return self.path == other.path
            

class Link:
    def __init__(self, target, alias=None):
        self.target = target
        self.alias = alias
        self.slug = slug_case(target)
        
    def md_link(self):
        """Returns a link string that follows the Markdown specification"""
        if self.alias:
            return md_link(self.alias, self.slug)
        else:
            return md_link(self.target, self.slug)
        
    def __eq__(self, other):
        return self.target == other.target