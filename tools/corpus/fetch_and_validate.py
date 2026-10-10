"""Download + validate the designer corpus. Stdlib-only (plus PyMuPDF if present).

Usage (Debian/LXDE):
    sudo apt install python3 poppler-utils   # poppler only needed as fallback
    python3 tools/corpus/fetch_and_validate.py [manifest] [outdir]

Writes outdir/corpus_report.csv with OK / OUT_OF_RANGE / ERROR per candidate,
checking the manifest band (pages + bytes), SHA-256, and embedded image codecs
(JPEG/JPX/JBIG2/CCITT/Flate) via PyMuPDF or `pdfimages -list`.
"""
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request

MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json")
MAX_BYTES = 60_000_000


def codecs_of(path):
    """Return sorted image-encoding names found in the PDF (best effort)."""
    try:
        import fitz
        doc = fitz.open(path)
        kinds = set()
        for pno in range(doc.page_count):
            for xref, *_ in doc[pno].get_images(full=True):
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                ext = (info.get("ext") or "").lower()
                if ext in ("jpg", "jpeg"):
                    kinds.add("JPEG")
                elif ext in ("jp2", "jpx"):
                    kinds.add("JPX")
                elif ext in ("jb2", "jbig2", "jb2e"):
                    kinds.add("JBIG2")
                elif ext in ("tif", "tiff"):
                    kinds.add("TIFF-G4?" if info.get("bpc") == 1 else "TIFF")
                elif ext == "png" or info.get("bpc") == 1:
                    kinds.add("Flate-1bit" if info.get("bpc") == 1 else "Flate")
                else:
                    kinds.add(ext.upper() or "RAW")
        doc.close()
        return ",".join(sorted(kinds)) if kinds else "none"
    except ImportError:
        pass
    if shutil.which("pdfimages"):
        try:
            out = subprocess.run(["pdfimages", "-list", path], capture_output=True,
                                 text=True, timeout=120).stdout
            encs = set()
            for line in out.splitlines()[2:]:
                parts = line.split()
                if len(parts) > 13:
                    encs.add(parts[13])
            return ",".join(sorted(encs)) if encs else "none"
        except Exception as e:  # noqa: BLE001
            return f"pdfimages-error:{e}"
    return "unknown"


def page_count(path):
    try:
        import fitz
        d = fitz.open(path)
        n = d.page_count
        d.close()
        return n
    except ImportError:
        pass
    if shutil.which("pdfinfo"):
        try:
            out = subprocess.run(["pdfinfo", path], capture_output=True,
                                 text=True, timeout=60).stdout
            for line in out.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":")[1])
        except Exception:  # noqa: BLE001
            pass
    return None


def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "pdf-minimalist-corpus/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        total = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                raise IOError(f"over {MAX_BYTES} byte cap")
            f.write(chunk)
    return total


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    manifest = sys.argv[1] if len(sys.argv) > 1 else MANIFEST
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join("tools", "corpus", "downloads")
    os.makedirs(outdir, exist_ok=True)
    spec = json.load(open(manifest))
    band = spec["band"]
    rows = []
    for rec in spec["records"]:
        dest = os.path.join(outdir, rec["file"])
        status, detail = "OK", ""
        try:
            nbytes = fetch(rec["url"], dest)
            npages = page_count(dest)
            if npages is None:
                status, detail = "ERROR", "unreadable pdf"
            elif not (band["min_pages"] <= npages <= band["max_pages"]
                      and band["min_bytes"] <= nbytes <= band["max_bytes"]):
                status = "OUT_OF_RANGE"
                detail = f"pages={npages} bytes={nbytes}"
            codecs = codecs_of(dest) if status == "OK" else ""
            rows.append({"file": rec["file"], "category": rec.get("category", ""),
                         "pages": npages or "", "bytes": nbytes,
                         "sha256": sha256(dest)[:16], "codecs": codecs,
                         "status": status, "detail": detail})
            print(f"{status:12} {rec['file']} pages={npages} bytes={nbytes} codecs={codecs} {detail}")
        except Exception as e:  # noqa: BLE001
            rows.append({"file": rec["file"], "category": rec.get("category", ""),
                         "pages": "", "bytes": "", "sha256": "", "codecs": "",
                         "status": "ERROR", "detail": str(e)[:120]})
            print(f"ERROR        {rec['file']}: {e}")
    csv_path = os.path.join(outdir, "corpus_report.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "category", "pages", "bytes",
                                          "sha256", "codecs", "status", "detail"])
        w.writeheader()
        w.writerows(rows)
    ok = sum(1 for r in rows if r["status"] == "OK")
    print(f"\n{ok}/{len(rows)} OK -> {csv_path}")


if __name__ == "__main__":
    main()
