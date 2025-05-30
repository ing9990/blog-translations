# 파일명: .github/scripts/generate_sidebar.py
import os

BASE_DIR = 'docs'
SIDEBAR_PATH = os.path.join(BASE_DIR, '_sidebar.md')


def format_title(name: str) -> str:
  """under_score 또는 kebab-case를 Title Case로 바꾸는 함수"""
  name = os.path.splitext(name)[0]  # .md 제거
  name = name.replace('_', ' ').replace('-', ' ')
  return name.title()  # 단어마다 첫 글자 대문자


def generate_sidebar():
  sidebar_lines = []

  for root, dirs, files in os.walk(BASE_DIR):
    rel_path = os.path.relpath(root, BASE_DIR)
    if rel_path == ".":
      continue  # docs/는 생략

    indent_level = rel_path.count(os.sep)
    indent = " " * 4 * indent_level

    folder = os.path.basename(root)
    folder_title = format_title(folder)
    sidebar_lines.append(f"{indent}- {folder_title}")

    for f in sorted(files):
      if f.endswith(".md") and not f.startswith("_"):
        filename = os.path.splitext(f)[0]
        file_title = format_title(filename)
        file_path = os.path.join(rel_path, f).replace('\\', '/')
        sidebar_lines.append(
          f"{indent}    - [{file_title}](/" + file_path + ")")

  with open(SIDEBAR_PATH, 'w', encoding='utf-8') as f:
    f.write("\n".join(sidebar_lines))
    print(f"✅ Sidebar generated at {SIDEBAR_PATH}")


if __name__ == "__main__":
  generate_sidebar()
