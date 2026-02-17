# key-notes

A super simple, minimal native desktop markdown notes app. Limited to 10 notes, stored locally.

## Features

- Markdown preview (live render)
- Mermaid diagram support
- Keyboard shortcuts
- Local file storage (plain `.md` files)

## Quick start

```
pip3 install pywebview
python3 main.py
```

## Keyboard shortcuts

| Action | Shortcut |
|--------|----------|
| Save | `Cmd/Ctrl + S` |
| Zoom in | `Cmd/Ctrl + =` |
| Zoom out | `Cmd/Ctrl + -` |
| Reset zoom | `Cmd/Ctrl + 0` |
| Indent | `Tab` |

## How it works

The app uses **pywebview** to open a native desktop window pointing at a built-in HTTP server. Notes are stored as `.md` files in a `notes/` folder (created automatically on first run with starter content).

## Stack

- Python 3
- [pywebview](https://pywebview.flowrl.com/)
- [marked.js](https://marked.js.org/)
- [mermaid.js](https://mermaid.js.org/)
