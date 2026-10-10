"""Assemble paper_v2/MANUSCRIPT_BUILD_GUIDE.md from guide_header.md + output/report_generated.md."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
header = (ROOT / "paper_v2/guide_header.md").read_text(encoding="utf-8")
body = (ROOT / "paper_v2/output/report_generated.md").read_text(encoding="utf-8")
out = ROOT / "paper_v2/MANUSCRIPT_BUILD_GUIDE.md"
out.write_text(header + body, encoding="utf-8")
print("wrote", out, (header + body).count("\n"), "lines")
