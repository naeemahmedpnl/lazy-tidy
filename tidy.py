import json, shutil, sys
from pathlib import Path
import ollama

MODEL = "gemma3:4b"
CATEGORIES = ["Documents", "Images", "Videos", "Audio",
              "Code", "Archives", "Installers", "Other"]

# Fast path: known extensions need no model at all.
EXT_MAP = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt",
                  ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".pages", ".numbers", ".key"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".svg", ".bmp", ".tiff"},
    "Videos": {".mp4", ".mov", ".mkv", ".avi", ".webm"},
    "Audio": {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp",
             ".go", ".rs", ".sh", ".json", ".yaml", ".yml", ".ipynb"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z", ".tgz"},
    "Installers": {".dmg", ".pkg", ".exe", ".msi", ".deb", ".apk"},
}

def by_extension(path: Path):
    ext = path.suffix.lower()
    for cat, exts in EXT_MAP.items():
        if ext in exts:
            return cat
    return None

def by_model(filename: str) -> str:
    prompt = (
        f"Categories: {CATEGORIES}\n"
        f"Pick the single best category for the file named: {filename}\n"
        'Reply only as JSON: {"category": "<one of the categories>"}'
    )
    try:
        r = ollama.chat(model=MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        format="json")
        cat = json.loads(r["message"]["content"]).get("category", "Other")
        return cat if cat in CATEGORIES else "Other"
    except Exception as e:
        print(f"  [model error: {e}]")
        return "Other"

def main():
    if len(sys.argv) < 2:
        print("Usage: python tidy.py <folder> [--apply]")
        sys.exit(1)
    folder = Path(sys.argv[1]).expanduser()
    apply = "--apply" in sys.argv
    stats = {"extension": 0, "model": 0}
    for f in sorted(folder.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        cat = by_extension(f)
        if cat:
            source = "extension"
        else:
            cat = by_model(f.name)
            source = "model"
        stats[source] += 1
        print(f"{f.name}  ->  {cat}/   [{source}]")
        if apply:
            dest = folder / cat / f.name
            dest.parent.mkdir(exist_ok=True)
            if dest.exists():
                dest = dest.with_name(f"{dest.stem}_dup{dest.suffix}")
            shutil.move(str(f), str(dest))
    print(f"\nDone: {stats['extension']} by extension, {stats['model']} by local model.")
    if not apply:
        print("Preview only. Re-run with --apply to move files.")

if __name__ == "__main__":
    main()
