import os
import urllib.parse

BASE_DIR = 'docs'
SIDEBAR_PATH = os.path.join(BASE_DIR, '_sidebar.md')


def format_title(name: str) -> str:
  """Convert the file name to Title Case and remove the file extension."""
  name = os.path.splitext(name)[0]
  name = name.replace('_', ' ').replace('-', ' ')
  return name


def generate_sidebar():
  sidebar_lines = []

  for root, dirs, files in os.walk(BASE_DIR):
    rel_path = os.path.relpath(root, BASE_DIR)
    if rel_path == ".":
      continue

    indent_level = rel_path.count(os.sep)
    indent = " " * 4 * indent_level

    folder_title = format_title(os.path.basename(root))
    sidebar_lines.append(f"{indent}- {folder_title}")

    for f in sorted(files):
      if f.endswith(".md") and not f.startswith("_"):
        filename = os.path.splitext(f)[0]
        file_title = format_title(filename)
        file_path = os.path.join(rel_path, f).replace('\\', '/')
        encoded_file_path = urllib.parse.quote(file_path)
        sidebar_lines.append(
            f"{indent}    - [{file_title}](/" + encoded_file_path + ")")

  with open(SIDEBAR_PATH, 'w', encoding='utf-8') as f:
    f.write("\n".join(sidebar_lines))
    print(f"Sidebar generated at {SIDEBAR_PATH}")


if __name__ == "__main__":
  generate_sidebar()
