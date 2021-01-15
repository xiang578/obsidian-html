<div align="center"><b>NOTE</b>: <code>obsidian-html</code> has been renamed to <code>oboe</code> in order to gradually decouple it from Obsidian. Apologies for the inconveniences this may cause. If you've already installed <code>obsidian-html</code>, you can uninstall it and follow the <a href="#installation">installation instructions</a> for <code>oboe</code> below. Be sure to also update your GitHub Actions.</div>

<br>

<div align="center"><h1>Oboe</h1></div>

<p align="center">
  <a href="#installation">Installation</a> -
  <a href="#usage">Usage</a> -
  <a href="#tips">Tips</a> 
</p>

## Installation

1. Make sure Python and PIP are installed.
2. Install Oboe with `pip install git+https://github.com/kmaasrud/oboe`

## Usage

Supply the path to an Obsidian vault, and Oboe will convert all its notes into HTML, appended by the notes' backlinks. 

    oboe <path to vault>

These HTML-files are by default placed in the directory `./html`. To specify another output directory, use the flag `-o` or `--output-directory`.

    oboe <path to vault> -o <output directory>
    
### Sub-directories

By default, Oboe only converts notes in the vault root, and not those inside sub-directories. To include sub-directories, add them with the flag `-d` or `--sub-directories`. For example, say you have the folders `Daily notes` and `Zettels` that you want to have converted. In this case, run

    oboe <path to vault> -d "Daily notes" "Zettels"
    
### Templates

The output is not very exciting from the get-go. It needs some style and structure. This is done by using a HTML template. A template must have the formatters `{title}` and `{content}` present. Their value should be obvious. The template file is supplied to `obsidian-html` by the flag `-t` or `--template`, like this:

    oboe <path to vault> -t template.html

Here you can add metadata, link to CSS-files and add unified headers/footers to all the pages. [Here's](https://github.com/kmaasrud/brain/blob/master/template.html) an example of how I use the template function on my own hosted vault.

Note that because of the way Python does formatting, the template cannot contain single curly braces other than the abovementioned formatters. To include Javascript or CSS in your template, always use double curly braces (e.g. `{{`). These will be changed into single braces in the final result.

### Filtering notes by tag

Oboe supports only converting notes that contain a certain tag. The filter is specified via the `-f` or `--filter` flag. For example, say you had a tag `#physics` for notes relating to physics, and the same for `#chemistry`. To convert all notes relating to both physics and chemistry, run Oboe like this:

    oboe <path to vault> -f physics chemistry

### Other flags

- `-e` or `--add-file-extensions`: Most web-servers do not need the `.html` file extension in URLs to find the correct file. However, that might be needed when browsing the converted vault locally. If you experience issues with this or want all links to have a `.html` extension, just add this flag when running.

## Tips