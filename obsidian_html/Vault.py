import os
import regex as re
from obsidian_html.utils import slug_case, md_link, render_markdown
from obsidian_html.Note import Note


class Vault:
    def __init__(self, vault_root, extra_folders=[], html_template=None, filter=[]):
        self.vault_root = vault_root
        self.filter = filter
        self.notes = find_files(self, vault_root, extra_folders)
        self.extra_folders = extra_folders
        self._add_backlinks()

        self.html_template = html_template
        if html_template:
            with open(html_template, "r", encoding="utf8") as f:
                self.html_template = f.read()

    def _add_backlinks(self):
        for i, note in enumerate(self.notes):
            # Make temporary list of all notes except current note in loop
            others = [other for other in self.notes if other != note]
            backlinks = self.notes[i].find_backlinks(others)
            if backlinks:
                self.notes[i].backlinks += "\n<div class=\"backlinks\" markdown=\"1\">\n"
                for backlink in backlinks:
                    self.notes[i].backlinks += f"- {backlink.md_link()}\n"
                self.notes[i].backlinks += "</div>"

                self.notes[i].backlinks = render_markdown(self.notes[i].backlinks)

    def export_html(self, out_dir):
        # Default location of exported HTML is "html"
        if not out_dir:
            out_dir = os.path.join(self.vault_root, "html")
        # Ensure out_dir exists, as well as its sub-folders.
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for folder in self.extra_folders:
            if not os.path.exists(os.path.join(out_dir, folder)):
                os.makedirs(os.path.join(out_dir, folder))

        for note in self.notes:
            if self.html_template:
                html = self.html_template.format(title=note.title, content=note.html(), backlinks=note.backlinks)
            else:
                html = note.html()
            with open(os.path.join(out_dir, note.filename_html), "w", encoding="utf8") as f:
                f.write(html)


def find_files(self, vault_root, extra_folders):
    # Find all markdown-files in vault root.
    md_files = find_md_files(self, vault_root)

    # Find all markdown-files in each extra folder.
    for folder in extra_folders:
        md_files += find_md_files(self, os.path.join(vault_root, folder), is_extra_dir=True)

    return md_files


def find_md_files(self, root, is_extra_dir=False):
    md_files = []
    for md_file in os.listdir(root):
        # Check if the element in 'root' has the extension .md and is indeeed a file
        if not (md_file.endswith(".md") and os.path.isfile(os.path.join(root, md_file))):
            continue
        
        with open(os.path.join(root, md_file), encoding="utf8") as f:
            document = f.read()
        
        include = False

        for f in self.filter:
            if document.find("#"+f) > -1:
                include = True
        
        if not include:
            continue
        
        md_files.append(Note(os.path.join(root, md_file), is_extra_dir=is_extra_dir))

    return md_files