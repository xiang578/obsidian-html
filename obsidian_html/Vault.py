import os
from obsidian_html.utils import slug_case, md_link
from obsidian_html.Note import Note


class Vault:
    def __init__(self, vault_root, extra_folders=[], html_template=None):
        self.vault_root = vault_root
        self.notes = find_files(vault_root, extra_folders, no_extension=True)
        self.extra_folders = extra_folders
        self._add_backlinks()

        self.html_template = html_template
        if html_template:
            with open(html_template) as f:
                self.html_template = f.read()

    def _add_backlinks(self):
        for i, note in enumerate(self.notes):
            # Make temporary list of all notes except current note in loop
            others = self.notes; others.remove(note)
            backlinks = self.notes[i].find_backlinks(others)
            if backlinks:
                self.notes[i].content += "\n<div class=\"backlinks\" markdown=\"1\">\n## Backlinks\n\n"
                for backlink in backlinks:
                    self.notes[i].content += f"- {backlink.md_link()}\n"
                self.notes[i].content += "</div>"


    def export_html(self, out_dir):
        # Default location of exported HTML is "html"
        if not out_dir:
            out_dir = os.path.join(self.vault_root, "html")
        # Ensure out_dir exists, as well as its sub-folders.
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for folder in self.extra_folders:
            if not os.path.exists(out_dir + "/" + folder):
                os.makedirs(out_dir + "/" + folder)

        for note in self.notes:
            if self.html_template:
                html = self.html_template.format(title=note.filename_no_ext, content=note.html())
            else:
                html = note.html()
            with open(os.path.join(out_dir, note.filename_html), "w") as f:
                f.write(html)


def find_files(vault_root, extra_folders, no_extension=False):
    # Find all markdown-files in vault root.
    md_files = find_md_files(vault_root, no_extension)

    # Find all markdown-files in each extra folder.
    for folder in extra_folders:
        md_files += find_md_files(os.path.join(vault_root, folder), no_extension, is_extra_dir=True)

    return md_files


def find_md_files(root, no_extension, is_extra_dir=False):
    md_files = []
    for md_file in os.listdir(root):
        # Check if the element in 'root' has the extension .md and is indeeed a file
        if not (md_file.endswith(".md") and os.path.isfile(os.path.join(root, md_file))):
            continue
        
        """
        with open(os.path.join(root, md_file), encoding="utf8") as f:
            content = f.read()

        if no_extension:
            md_file = md_file.replace(".md", "")

        if is_extra_folder:
            md_file = os.path.join(os.path.split(root)[-1], md_file)

        """
        md_files.append(Note(os.path.join(root, md_file), is_extra_dir=is_extra_dir))

    return md_files