import os
import regex as re
from obsidian_html.utils import slug_case, md_link


class Note:
    def __init__(self, path, is_extra_dir = False):
        self.full_path = path
        self.filename = os.path.split(path)[-1]
        self.filename_no_ext = self.filename.replace(".md", "")
        self.is_extra_dir = is_extra_dir
        with open(path, encoding="utf8") as f:
            self.content = f.read()
            
    def links_in_file(self):
        matches = re.finditer(r"\[{2}([^\]]*?)[|#\]]([^\]]*?)\]+", self.content)

        links = []
        for match in matches:
            link = Link(match.group(1), alias=match.group(2))
            links.append(link)

        return links
    
    def find_backlinks(self, others):
        backlinks = []
        for other in others:
            link_targets = [link.target for link in other.links_in_file()]
            if self.filename_no_ext in link_targets:
                backlinks.append(Link(other.filename_no_ext))

        backlinks = sorted(backlinks, key=lambda x: x.target)

        return backlinks
            

class Link:
    def __init__(self, target, alias=None, is_target_slug=False):
        self.target = target
        self.alias = alias
        self.is_target_slug = target == slug_case(target)
        self.slug = target if self.is_target_slug else slug_case(target)
        
    def md_link(self):
        if self.alias:
            return md_link(self.alias, self.slug)
        else:
            return md_link(self.target, self.slug)