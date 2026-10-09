"""Build a local demo PDF in ./.tmp/ (never /tmp)."""
import fitz

PAGES = [
    ("Scan test page 1 — hello world", False),
    ("Page 2 — faint notes 12345", False),
    ("Page 3 — BOLD HEADLINE plus body text", True),
]

d = fitz.open()
for title, _ in PAGES:
    p = d.new_page(width=500, height=650)
    p.insert_text((60, 120), title, fontsize=22)
    p.insert_text((60, 200), "The quick brown fox jumps over the lazy dog. " * 3, fontsize=11)
    p.draw_rect(fitz.Rect(60, 300, 440, 450))
d.save(".tmp/demo.pdf")
print(f"demo pages: {d.page_count} -> .tmp/demo.pdf")
