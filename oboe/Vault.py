import os
import regex as re
import json
from shutil import copytree
from oboe.utils import slug_case, md_link, render_markdown, write
from oboe.Note import Note


class Vault:
    def __init__(self, vault_root, extra_folders=[], html_template=None, filter=[]):
        self.vault_root = vault_root
        self.filter = filter
        self.extra_dir_index_content_map = {}
        self.notes = self._find_files(vault_root, extra_folders)
        self.extra_folders = extra_folders
        self._add_backlinks()

        self.html_template_path = os.path.abspath(html_template)
        if html_template:
            with open(html_template, "r", encoding="utf8") as f:
                self.html_template = f.read()


    def _add_backlinks(self):
        for i, note in enumerate(self.notes):
            # Make temporary list of all notes except current note in loop
            others = [other for other in self.notes if other != note]
            backlinks = self.notes[i].find_backlinks(others)
            if backlinks:
                self.notes[i].backlink_html += "\n<div class=\"backlinks\" markdown=\"1\">\n"
                for backlink in backlinks:
                    self.notes[i].backlink_html += f"- {backlink.md_link()}\n"
                self.notes[i].backlink_html += "</div>"

                self.notes[i].backlink_html = render_markdown(self.notes[i].backlink_html)


    def export_html(self, out_dir):
        # Ensure out_dir exists, as well as its sub-folders.
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for folder in self.extra_folders:
            if not os.path.exists(os.path.join(out_dir, folder)):
                os.makedirs(os.path.join(out_dir, folder))

        self._copy_assets(out_dir)

        if self.html_template:
            stylesheets = re.findall('<link+.*rel="stylesheet"+.*href="(.+?)"', self.html_template)
            for stylesheet in stylesheets:
                # Check if template contains reference to a stylesheet
                stylesheet_abspath = os.path.join(os.path.dirname(self.html_template_path), stylesheet)
                # Check if the referenced stylesheet is local, and copy it to out_dir if it is
                if os.path.isfile(stylesheet_abspath):
                    print("Copying local styleshit to the output directory") # TODO: Message system
                    with open(stylesheet_abspath, encoding="utf-8") as f:
                        stylesheet_content = f.read()
                    write(stylesheet_content, os.path.join(out_dir, stylesheet))

            # Use the supplied template on all notes
            for note in self.notes:
                note_html, note_metadata = note.html()
                html = self.html_template.format(title=note.title, content=note_html, backlinks=note.backlink_html)
                write(html, os.path.join(out_dir, note.extra_dir, note.filename_html))
                with open(os.path.join(out_dir, note.extra_dir, note.metadata_filename), 'w') as fp:
                    json.dump(note_metadata, fp)
        else:
            # Do not use a template, just output the content and a list of backlinks
            for note in self.notes:
                html = "{content}\n{backlinks}".format(content=note.html(), backlinks=note.backlink_html)
                write(html, os.path.join(out_dir, note.filename_html))
        if self.extra_dir_index_content_map:
            for sub_dir, content in self.extra_dir_index_content_map.items():
                write(content, os.path.join(out_dir, sub_dir, "index.html"))


    def _copy_assets(self, out_dir):
        assets_path = os.path.join(self.vault_root, "assets")
        dest_path = os.path.join(out_dir, "assets")
        if not os.path.exists(assets_path):
            return
        copytree(assets_path, dest_path, dirs_exist_ok=True)


    def _find_files(self, vault_root, extra_folders):
        # Find all markdown-files in vault root.
        md_files = self._find_md_files(vault_root)

        # Find all markdown-files in each extra folder.
        for folder in extra_folders:
            sub_dir_md_files = self._find_md_files(os.path.join(vault_root, folder), is_extra_dir=True)
            md_files += sub_dir_md_files
            self._gen_index(sub_dir_md_files)

        return md_files

    def _gen_index(self, notes):
        notes.sort(key = lambda n: os.stat(n.path).st_birthtime)
        note_list = ["""<li><a href="%s">%s</a></li>""" % (note.filename_html, note.title) for note in notes]
        container_str = """<div id="index"><ul>%s</ul></div>""" % "".join(note_list)
        self.extra_dir_index_content_map[notes[0].extra_dir] = container_str

    def _find_md_files(self, root, is_extra_dir=False):
        md_files = []
        for md_file in os.listdir(root):
            # Check if the element in 'root' has the extension .md and is indeeed a file
            if not (md_file.endswith(".md") and os.path.isfile(os.path.join(root, md_file))):
                continue

            note = Note(os.path.join(root, md_file), is_extra_dir=is_extra_dir)

            # Filter tags
            if self.filter:
                for tag in self.filter:
                    if tag in note.tags:
                        md_files.append(note)
                        break
            else:
                md_files.append(note)

        return md_files
