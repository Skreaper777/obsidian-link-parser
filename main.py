import csv
import re
from pathlib import Path
from collections import defaultdict, deque

# ========== НАСТРОЙКИ ==========
vault_path = Path(r"C:\Users\stasr\Documents\Obsidian Vault\obsidian-valut")
parent_note_relpath = Path(r"Теги\Навыки, личные качества, работа, профессия\__Навыки, личные качества, работа, профессия.md")
allow_dirs = {
    "Теги",
    "_Планировщик",
}
max_depth = 4  # Максимальная глубина рекурсивных ссылок
# ===============================

parent_note_stem = parent_note_relpath.stem
link_pattern = re.compile(r"\[\[([^\[\]|]+)(?:\|[^\]]*)?\]\]")

# 1. Построим карту ссылок: кто на кого ссылается
link_map = defaultdict(set)  # ключ: note, значение: set(на кого ссылается)

note_paths = {}  # имя → путь

for md_file in vault_path.rglob("*.md"):
    rel_path = md_file.relative_to(vault_path)
    if not any(part in allow_dirs for part in rel_path.parts):
        continue

    try:
        text = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️ Пропущен файл {rel_path} — ошибка чтения: {e}")
        continue

    from_note = md_file.stem
    note_paths[from_note] = rel_path
    links = link_pattern.findall(text)
    for to_note in links:
        link_map[to_note].add(from_note)

# 2. Рекурсивный сбор обратных ссылок с ограничением по глубине
result = set()
visited = set()
queue = deque([(parent_note_stem, 0)])

while queue:
    current, depth = queue.popleft()
    if depth >= max_depth:
        continue

    for backlink in link_map.get(current, []):
        if backlink not in visited:
            visited.add(backlink)
            result.add((parent_note_stem, backlink))
            queue.append((backlink, depth + 1))

# 3. Сохраняем в CSV (без preview)
output_csv = "backlinks_deep.csv"
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Target Note', 'Backlink From'])
    for target, source in sorted(result):
        writer.writerow([target, str(note_paths.get(source, source))])

print(f"✅ CSV-файл сохранён: {output_csv}")
