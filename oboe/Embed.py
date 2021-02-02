import regex as re
from oboe.utils import embed_image

LINK_SYNTAX = {
    "|": "resize",
    "#": "section",
    "#^": "blockref"
}

FILE_TYPE = {
    "image": ["png", "jpg", "jpeg", "gif", "bmp", "svg", "tiff"],
    "audio": ["mp3", "webm", "wav", "m4a", "ogg", "3gp", "flac"],
    "video": ["mp4", "webm", "ogv"],
    "doc": ["pdf"],
    "note": ["md"]
}

class Embed:
    def __init__(self, obsidian_link):
        self.obsidian_link = obsidian_link
        extended_link = re.match(r"([^#|^\n]+)([#|]\^?)(.*)", obsidian_link)
        if extended_link:
            self.file = extended_link.group(1)
            setattr(self, LINK_SYNTAX[extended_link.group(2)], extended_link.group(3))
        else:
            self.file = obsidian_link
        for ft, exts in FILE_TYPE.items():
            if any([(".%s" % ext) in obsidian_link for ext in exts]):
                setattr(self, "file_type", ft)
                break
        self.link = "notes/assets/%s" % self.file

    def md_embed(self):
        """Returns a link string that follows the Markdown specification"""
        if getattr(self, "file_type") == "image":
            if hasattr(self, "resize"):
                resize = getattr(self, "resize")
                return embed_image(self.link, resize)
            return embed_image(self.link, None)


    def __eq__(self, other):
        return self.obsidian_link == other.obsidian_link
