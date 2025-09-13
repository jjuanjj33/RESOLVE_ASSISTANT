import fitz, json
from settings import *

doc = fitz.open(PDF_PATH)

chunks = []
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text("text")
    if text.strip():
        chunk = {"page": page_num + 1,
                 "text": text.strip()}
        chunks.append(chunk)

with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)