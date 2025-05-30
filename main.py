import csv
import re
from pathlib import Path
from collections import defaultdict
import yaml

# ========== НАСТРОЙКИ ==========
vault_path = Path(r"C:\Users\stasr\Documents\Obsidian Vault\obsidian-valut")
parent_note_relpath = Path(r"Теги\Навыки, личные качества, работа, профессия\__Навыки, личные качества, работа, профессия.md")
allow_dirs = {
    "Теги",
    "_Планировщик",
    "_WiKi",
}
max_depth = 5
yaml_stop_keys = {"Тип-записи"}

value_by = {
    "yaml_key": "Приоритет",
    "map": {
        "6) Очень низкий 🟤": 1.0,
        "5) Низкий 🔵": 2.0,
        "4) Обычный 🟢": 5.0,
        "3) Важный 🟡": 8.0,
        "2) Очень важный 🟠": 11.0,
        "1) Критически важный 🔴": 15.0
    }
}

# ===============================

parent_note_stem = parent_note_relpath.stem
link_pattern = re.compile(r"\[\[([^\[\]|]+)(?:\|[^\]]*)?\]\]")

link_map = defaultdict(set)
note_paths = {}
stop_nodes = set()
yaml_values = {}

for md_file in vault_path.rglob("*.md"):
    rel_path = md_file.relative_to(vault_path)
    if not any(part in allow_dirs for part in rel_path.parts):
        continue

    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️ Пропущен файл {rel_path} — ошибка чтения: {e}")
        continue

    from_note = md_file.stem
    note_paths[from_note] = rel_path

    # Парсим YAML вручную
    if content.startswith('---'):
        try:
            yaml_text = content.split('---', 2)[1]
            metadata = yaml.safe_load(yaml_text)
            if isinstance(metadata, dict):
                if any(k in metadata for k in yaml_stop_keys):
                    stop_nodes.add(from_note)

                # Если value_by включён — сохраняем значение
                if value_by:
                    val = metadata.get(value_by["yaml_key"])
                    yaml_values[from_note] = value_by["map"].get(val, 0.0)
        except Exception:
            pass  # пропускаем YAML

    # Ищем ссылки
    links = link_pattern.findall(content)
    for to_note in links:
        link_map[to_note].add(from_note)

# Рекурсивная сборка путей
def collect_paths(current, path, depth, results):
    if depth >= max_depth:
        results.append(path)
        return
    if current in stop_nodes:
        results.append(path)
        return
    backlinks = link_map.get(current, [])
    if not backlinks:
        results.append(path)
    else:
        for b in backlinks:
            if b in path:
                continue
            collect_paths(b, path + [b], depth + 1, results)

all_paths = []
collect_paths(parent_note_stem, [parent_note_stem], 0, all_paths)

# Сохраняем CSV
output_csv = "link_hierarchy.csv"
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    header = []
    if value_by:
        header.append("Value")
    header += [f"Level {i}" for i in range(max_depth + 1)]
    writer.writerow(header)

    for path in all_paths:
        row = path + [''] * (max_depth + 1 - len(path))
        if value_by:
            last_node = row[-1] or row[-2]  # последний непустой
            value = yaml_values.get(last_node, 0.0)
            writer.writerow([value] + row)
        else:
            writer.writerow(row)

print(f"✅ CSV-файл сохранён: {output_csv}")
