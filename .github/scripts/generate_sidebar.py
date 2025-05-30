import os

BASE_DIR = 'docs'
SIDEBAR_FILE = os.path.join(BASE_DIR, '_sidebar.md')

def format_title(name):
    """파일명 또는 폴더명을 타이틀형으로 변환"""
    name = os.path.splitext(name)[0]  # .md 제거
    return name.replace('-', ' ').replace('_', ' ').title()

def generate_sidebar():
    sidebar_lines = []

    for root, dirs, files in os.walk(BASE_DIR):
        rel_path = os.path.relpath(root, BASE_DIR)
        if rel_path == '.':
            continue

        indent_level = rel_path.count(os.sep)
        indent = '  ' * indent_level
        folder_name = os.path.basename(root)
        sidebar_lines.append(f'{indent}- {folder_name}')

        for file in sorted(files):
            if file.endswith('.md') and not file.startswith('_'):
                file_path = os.path.join(rel_path, file).replace('\\', '/')
                title = format_title(file)
                sidebar_lines.append(f'{indent}  - [{title}](/' + file_path + ')')

    with open(SIDEBAR_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sidebar_lines))
        print(f"✅ Generated: {SIDEBAR_FILE}")

if __name__ == "__main__":
    generate_sidebar()
