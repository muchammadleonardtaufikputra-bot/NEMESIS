
"""
NEMESIS CORE
Unified Report Export Generator

Creates JSON and HTML exports from the unified security report.
Read-only source access. Export files are written to REPORTS_DIR.
"""

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import quote

from config import REPORTS_DIR
from modules.unified_reporting.report_engine import (
    generate_unified_report,
)


EXPORT_PREFIX = "nemesis_unified_"


def _timestamp():
    """Return a filesystem-safe UTC timestamp."""
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )


def _export_filename(extension):
    if extension not in {"json", "html"}:
        raise ValueError("Unsupported export format.")

    return f"{EXPORT_PREFIX}{_timestamp()}.{extension}"


def generate_unified_json_export():
    """Generate a JSON export and return its Path."""
    report = generate_unified_report()

    if not isinstance(report, dict) or not report.get("success"):
        raise ValueError("Unified report generation failed.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = _export_filename("json")
    output_path = REPORTS_DIR / filename

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    return output_path


def _render_summary(report):
    summary = report.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    rows = []

    for key, value in summary.items():
        rows.append(
            "<tr>"
            f"<th>{escape(str(key.replace('_', ' ').title()))}</th>"
            f"<td>{escape(str(value))}</td>"
            "</tr>"
        )

    if not rows:
        return "<p>No summary data available.</p>"

    return (
        "<table><thead><tr><th>Metric</th><th>Value</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _render_scenarios(report):
    analytics = report.get("analytics", {})
    if not isinstance(analytics, dict):
        analytics = {}

    scenarios = analytics.get("scenario_detection_stats", {})
    if not isinstance(scenarios, dict) or not scenarios:
        return "<p>No scenario statistics available.</p>"

    rows = []

    for scenario, stats in sorted(scenarios.items()):
        if not isinstance(stats, dict):
            continue

        values = [
            scenario.replace("_", " ").upper(),
            stats.get("total", 0),
            stats.get("detected", 0),
            stats.get("not_detected", 0),
            stats.get("ignored", 0),
        ]

        rows.append(
            "<tr>"
            + "".join(
                f"<td>{escape(str(value))}</td>"
                for value in values
            )
            + "</tr>"
        )

    return (
        "<table><thead><tr>"
        "<th>Scenario</th><th>Total</th><th>Detected</th>"
        "<th>Not detected</th><th>Ignored</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _render_mitre_candidates(report):
    analytics = report.get("analytics", {})
    if not isinstance(analytics, dict):
        analytics = {}

    mappings = analytics.get("mitre_candidate_mappings", [])

    if not isinstance(mappings, list) or not mappings:
        return "<p>No candidate mappings available.</p>"

    rows = []

    for item in mappings:
        if not isinstance(item, dict):
            continue

        values = [
            item.get("scenario_id", ""),
            item.get("technique_id", ""),
            item.get("technique_name", ""),
            item.get("mapping_status", ""),
            item.get("confidence", ""),
        ]

        rows.append(
            "<tr>"
            + "".join(
                f"<td>{escape(str(value))}</td>"
                for value in values
            )
            + "</tr>"
        )

    return (
        "<table><thead><tr>"
        "<th>Scenario</th><th>Technique ID</th>"
        "<th>Technique</th><th>Status</th><th>Confidence</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _render_limitations(report):
    limitations = report.get("limitations", [])

    if not isinstance(limitations, list) or not limitations:
        return "<p>No limitation details provided.</p>"

    items = []

    for item in limitations:
        items.append(f"<li>{escape(str(item))}</li>")

    return "<ul>" + "".join(items) + "</ul>"


def generate_unified_html_export():
    """Generate a standalone HTML report and return its Path."""
    report = generate_unified_report()

    if not isinstance(report, dict) or not report.get("success"):
        raise ValueError("Unified report generation failed.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = escape(str(report.get("generated_at", "N/A")))
    report_type = escape(str(report.get("report_type", "NEMESIS REPORT")))

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEMESIS Unified Security Report</title>
<style>
:root {{
    color-scheme: dark;
    --background: #07090e;
    --panel: #10141d;
    --border: #30394a;
    --text: #e8edf5;
    --muted: #a0aabd;
    --red: #ff1744;
    --green: #00e676;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    padding: 32px;
    background: var(--background);
    color: var(--text);
    font-family: Consolas, Arial, sans-serif;
}}
main {{ max-width: 1100px; margin: auto; }}
h1, h2 {{ color: var(--red); }}
h1 {{ letter-spacing: 3px; }}
h2 {{
    margin-top: 32px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}}
p, li {{ line-height: 1.6; color: var(--muted); }}
.panel {{
    padding: 20px;
    margin: 20px 0;
    background: var(--panel);
    border: 1px solid var(--border);
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    overflow-wrap: anywhere;
}}
th, td {{
    padding: 11px;
    text-align: left;
    border: 1px solid var(--border);
}}
th {{ color: var(--red); background: #151b26; }}
td {{ color: var(--text); }}
.notice {{
    padding: 15px;
    border-left: 3px solid var(--green);
    background: #07160f;
}}
footer {{
    margin-top: 40px;
    padding-top: 15px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 12px;
}}
@media(max-width:700px) {{
    body {{ padding: 15px; }}
    .panel {{ overflow-x: auto; }}
}}
</style>
</head>
<body>
<main>
    <h1>NEMESIS</h1>
    <p>ADVERSARY RESEARCH &amp; EMULATION SYSTEM</p>

    <div class="panel">
        <h2>REPORT INFORMATION</h2>
        <p><strong>Report type:</strong> {report_type}</p>
        <p><strong>Generated at:</strong> {generated_at}</p>
        <p><strong>Scope:</strong> Local read-only checks and inert simulations</p>
    </div>

    <h2>UNIFIED SECURITY SUMMARY</h2>
    <div class="panel">
        {_render_summary(report)}
    </div>

    <h2>SCENARIO PERFORMANCE</h2>
    <div class="panel">
        {_render_scenarios(report)}
    </div>

    <h2>MITRE ATT&amp;CK CANDIDATE MAPPINGS</h2>
    <div class="panel">
        {_render_mitre_candidates(report)}
        <p>These are candidate references, not confirmed attack evidence.</p>
    </div>

    <h2>REPORT LIMITATIONS</h2>
    <div class="panel">
        {_render_limitations(report)}
    </div>

    <div class="notice">
        Detection coverage represents stored inert simulation records only.
        It does not measure real-world threat detection effectiveness.
    </div>

    <footer>
        NEMESIS — Locally generated security report.
        Keep exported files private because they may contain local system
        assessment information.
    </footer>
</main>
</body>
</html>
"""

    filename = _export_filename("html")
    output_path = REPORTS_DIR / filename

    output_path.write_text(document, encoding="utf-8")

    return output_path


def list_unified_exports(limit=50):
    """List generated unified exports without exposing filesystem paths."""
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 50

    limit = max(1, min(limit, 100))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    exports = []

    for path in REPORTS_DIR.iterdir():
        if not path.is_file():
            continue

        if not path.name.startswith(EXPORT_PREFIX):
            continue

        if path.suffix.lower() not in {".json", ".html"}:
            continue

        try:
            stat = path.stat()
        except OSError:
            continue

        exports.append({
            "name": path.name,
            "format": path.suffix.lower().lstrip(".").upper(),
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(
                stat.st_mtime,
                timezone.utc,
            ).isoformat(),
            "download_url": (
                "/api/reports/unified/download/"
                + quote(path.name)
            ),
        })

    exports.sort(
        key=lambda item: item["modified_at"],
        reverse=True,
    )

    return exports[:limit]
