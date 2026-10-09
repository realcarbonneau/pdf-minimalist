"""Contact sheet: first page of every example -> ./.tmp/contact.png for review."""
import glob
import os

import fitz
from PIL import Image

files = sorted(glob.glob("examples/*.pdf"))
thumbs = []
for f in files:
    try:
        d = fitz.open(f)
        pix = d[0].get_pixmap(dpi=60, colorspace=fitz.csRGB, alpha=False)
        import numpy as np
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        img = Image.fromarray(arr)
        img.thumbnail((220, 280), Image.LANCZOS)
        thumbs.append((os.path.basename(f), img))
        d.close()
    except Exception as e:  # noqa: BLE001
        print("ERR", f, str(e)[:80])

cols = 7
cw, ch = 240, 330
rows = (len(thumbs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw, rows * ch), "white")
from PIL import ImageDraw
dr = ImageDraw.Draw(sheet)
for i, (name, t) in enumerate(thumbs):
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(t, (x + (cw - t.width) // 2, y + 8))
    dr.text((x + 6, y + ch - 22), name[:30], fill="black")
sheet.save(".tmp/contact.png")
print(f"{len(thumbs)} thumbs -> .tmp/contact.png")
