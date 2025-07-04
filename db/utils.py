import re
from models.models import ChatStructure

def load_title_description_pairs(filepath="contexto.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Divide usando títulos do tipo ### Pergunta
    parts = re.split(r'^###\s+', content, flags=re.MULTILINE)
    entries = []

    for part in parts[1:]:  # ignorar cabeçalho inicial
        lines = part.strip().split("\n", 1)
        if len(lines) == 2:
            title = lines[0].strip()
            description = lines[1].strip()
            entries.append((title, description))

    return entries

def save_new_entries_to_mongo(entries):
    count = 0
    for title, description in entries:
        if not ChatStructure.objects(title=title).first():
            ChatStructure(title=title, description=description).save()
            count += 1
    print(f"{count} novos itens foram salvos no MongoDB.")

