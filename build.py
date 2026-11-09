"""Fill shared blocks (icon sprite, Wächter flow) from index.html into the extra pages."""
from pathlib import Path
import re
ROOT = Path(__file__).parent
idx = (ROOT / "index.html").read_text(encoding="utf-8")

sprite = re.search(r'<svg width="0" height="0".*?</svg>', idx, re.S).group(0)
start = idx.index('<div class="ek-ablauf">')
end = idx.index('<div class="row row-cols-1 row-cols-lg-3 gx-5 gy-4 ek-ablauf__fakten">')
ablauf = idx[start:end].rstrip()
assert ablauf.endswith("</div>")

for name in ("styletile.html", "waechter.html"):
    tpl = (ROOT / "vorlagen" / name).read_text(encoding="utf-8")
    out = tpl.replace("<!--SPRITE-->", sprite).replace("<!--ABLAUF-->", ablauf)
    (ROOT / name).write_text(out, encoding="utf-8")
    print("built", name)
