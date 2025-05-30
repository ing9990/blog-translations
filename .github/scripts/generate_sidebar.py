import os

BASE_DIR = 'docs'
SIDEBAR_FILE = os.path.join(BASE_DIR, '_sidebar.md')

def generate_sidebar():
    sidebar_lines = []

    for root, dirs, files in os.walk(BASE_DIR):
        level = root.replace(BASE_DIR, '').count(os.sep)
        indent = '  ' * level

        md_files = [f for f in files if f.endswith('.md') and not f.startswith('_')]
        rel_root = root.replace(BASE_DIR + '/', '')

        for md in sorted(md_files):
            path = os.path.join(rel_root, md).replace('\\', '/')
            link_text = os.path.splitext(md)[0].replace('-', ' ').title()
            sidebar_lines.append(f"{indent}- [{link_text}](/{path})")

    with open(SIDEBAR_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sidebar_lines))
        print(f"✅ Generated: {SIDEBAR_FILE}")

if __name__ == "__main__":
    generate_sidebar()
