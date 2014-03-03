## Synopsis

This project contains Python code for parsing monospaced sheet music with chords and lyrics and producing html output. The objective is to allow for WYSIWYG editing with pretty html output. Currently, it does the job most of the time, but it relies on assumptions about the input, such as never having chords and text on the same line, preceding a song with the title and other metadata, and so on. It also has limited support for transposition, but lacks smart features such as key-guessing and choosing sharps and flats based on the key context.

## Example Usage
```python song_parser.py example_song > example_html```
