# lazy-tidy

A tiny, offline file tidier. It sorts a messy folder into category
folders using known file extensions first, and asks a local open-weight
model (Gemma 3 4B via Ollama) only when the extension tells it nothing.

No cloud, no API key, no cost. Your file names never leave your machine.

## Setup

```bash
brew install ollama && brew services start ollama
ollama pull gemma3:4b
python3 -m venv .venv && source .venv/bin/activate
pip install ollama
```

## Usage

```bash
python tidy.py ~/Downloads            # preview only
python tidy.py ~/Downloads --apply    # actually move files
```

Each line shows where a file goes and who decided: `[extension]` or `[model]`.

## Limitations

- The model only sees file names, not contents.
- Extensionless or unusual files can be misfiled (a `data.bin` went to Archives in my test).
- Name clashes get a `_dup` suffix. There is no undo, so always preview first.
- Only top-level files are handled, not subfolders.
