import csv
import re
from pathlib import Path
from collections import defaultdict

# ========== НАСТРОЙКИ ==========
vault_path = Path(r"C:\Users\stasr\Documents\Obsidian Vault\obsidian-valut")
parent_note_relpath = Path(r"Теги\Навыки, личные качества, работа, профессия\__Навыки, личные качества, работа, профессия.md")
allow_dirs = {
    "Теги",
    "_Планировщик",
    "_WiKi",
}
max_depth = 5
# ===============================

parent_note_stem = parent_note_relpath.stem
link_pattern = re.compile(r"\[\[([^\[\]|]+)(?:\|[^\]]*)?\]\]")

# Карта: кто на кого ссылается
link_map = defaultdict(set)
note_paths = {}

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

# Рекурсивно собираем все цепочки до max_depth
def collect_paths(current, path, depth, results):
    if depth > max_depth:
        return
    backlinks = link_map.get(current, [])
    if not backlinks:
        results.append(path)
    else:
        for b in backlinks:
            if b in path:
                continue  # защита от циклов
            collect_paths(b, path + [b], depth + 1, results)

# Запуск
all_paths = []
collect_paths(parent_note_stem, [parent_note_stem], 0, all_paths)

# Сохраняем в CSV
output_csv = "link_hierarchy.csv"
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    header = [f"Level {i}" for i in range(max_depth + 1)]
    writer.writerow(header)
    for path in all_paths:
        row = path + [''] * (max_depth + 1 - len(path))  # заполнение пустых ячеек
        writer.writerow(row)

print(f"✅ CSV-файл сохранён: {output_csv}")
