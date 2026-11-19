
import json
import sqlite3
import html

from datetime import datetime
from pathlib import Path

from config import REPORTS_DIR
from modules.assessment.assessment_database import DB_PATH


def get_assessment_record(record_id):
    """Retrieve one assessment record from SQLite."""

    if (
        not isinstance(record_id, int)
        or isinstance(record_id, bool)
        or record_id < 1
    ):
        raise ValueError("Record ID must be a positive integer.")

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT id, timestamp, assessment, total_checks,
                   pass_count, warning_count, error_count, result_json
            FROM security_assessments
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

        if row is None:
            raise ValueError(
                f"Assessment record {record_id} was not found."
            )

        record = dict(row)
        record["result"] = json.loads(record.pop("result_json"))

        return record

    finally:
        connection.close()


def build_report(record):
    """Build a structured assessment report."""

    result = record["result"]
    checks = result.get("checks", {})

    info_count = sum(
        1
        for check in checks.values()
        if str(check.get("status", "")).upper() == "INFO"
    )

    recommendations = []

    for name, check in checks.items():
        status = str(check.get("status", "")).upper()

        if status == "WARNING":
            recommendations.append({
                "check": name,
                "priority": "REVIEW",
                "recommendation": (
                    f"Review the {name.replace('_', ' ')} "
                    "configuration and investigate the warning."
                )
            })

        elif status in ("ERROR", "UNSUPPORTED"):
            recommendations.append({
                "check": name,
                "priority": "INVESTIGATE",
                "recommendation": (
                    f"Investigate why the {name.replace('_', ' ')} "
                    "check could not complete successfully."
                )
            })

    if not recommendations:
        recommendations.append({
            "check": "general",
            "priority": "INFORMATIONAL",
            "recommendation": (
                "No warning or error was reported by the completed "
                "checks. Continue regular security reviews and keep "
                "Windows and security definitions updated."
            )
        })

    return {
        "report": {
            "application": "NEMESIS",
            "report_type": "LOCAL SECURITY ASSESSMENT",
            "generated_at": datetime.now().isoformat(),
            "assessment_id": record["id"],
            "assessment_name": record["assessment"],
            "assessment_timestamp": record["timestamp"]
        },
        "summary": {
            "total_checks": record["total_checks"],
            "pass": record["pass_count"],
            "warning": record["warning_count"],
            "error": record["error_count"],
            "info": info_count
        },
        "checks": checks,
        "recommendations": recommendations
    }


def generate_json_report(record_id):
    """Generate and save a JSON assessment report."""

    record = get_assessment_record(record_id)
    report = build_report(record)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = (
        REPORTS_DIR / f"assessment_{record_id}.json"
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_path


def generate_html_report(record_id):
    """Generate and save a standalone HTML assessment report."""

    record = get_assessment_record(record_id)
    report = build_report(record)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    summary = report["summary"]

    rows = []

    for name, check in report["checks"].items():
        status = html.escape(
            str(check.get("status", "UNKNOWN"))
        )

        check_name = html.escape(
            name.replace("_", " ").upper()
        )

        details = html.escape(
            json.dumps(
                check.get("details", {}),
                indent=2,
                ensure_ascii=False
            )
        )

        rows.append(
            f"""
            <tr>
                <td>{check_name}</td>
                <td><strong>{status}</strong></td>
                <td><pre>{details}</pre></td>
            </tr>
            """
        )

    recommendation_items = []

    for item in report["recommendations"]:
        recommendation_items.append(
            "<li>"
            f"<strong>{html.escape(item['priority'])}</strong>: "
            f"{html.escape(item['recommendation'])}"
            "</li>"
        )

    report_info = report["report"]

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEMESIS Assessment Report #{record_id}</title>

<style>
body {{
    margin: 0;
    padding: 35px;
    background: #080d17;
    color: #dce7f5;
    font-family: Arial, sans-serif;
}}

.container {{
    max-width: 1100px;
    margin: auto;
}}

header {{
    border-bottom: 2px solid #00e5ff;
    padding-bottom: 20px;
    margin-bottom: 30px;
}}

h1 {{
    color: #00e5ff;
    letter-spacing: 4px;
}}

h2 {{
    color: #00e5ff;
    margin-top: 35px;
}}

.card {{
    background: #111c2d;
    border: 1px solid #263a50;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}}

.metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 12px;
}}

.metric {{
    background: #0b1422;
    padding: 15px;
    border-radius: 8px;
}}

.metric strong {{
    display: block;
    font-size: 28px;
    margin-top: 8px;
}}

.pass {{ color: #42e695; }}
.warning {{ color: #ffc857; }}
.error {{ color: #ff647c; }}
.info {{ color: #62b8ff; }}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    text-align: left;
    padding: 12px;
    border-bottom: 1px solid #263a50;
    vertical-align: top;
}}

pre {{
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    color: #a9c2d9;
}}

li {{
    margin-bottom: 12px;
    line-height: 1.5;
}}

footer {{
    margin-top: 40px;
    color: #8294a8;
    border-top: 1px solid #263a50;
    padding-top: 20px;
}}

@media print {{
    body {{
        background: white;
        color: #111;
        padding: 10px;
    }}

    .card, .metric {{
        background: white;
        border: 1px solid #ccc;
    }}

    h1, h2 {{
        color: #075985;
    }}

    pre {{
        color: #222;
    }}
}}
</style>
</head>

<body>
<div class="container">

<header>
    <h1>NEMESIS</h1>
    <h2>LOCAL SECURITY ASSESSMENT REPORT</h2>
    <p>Assessment ID: #{record_id}</p>
    <p>Generated: {html.escape(report_info["generated_at"])}</p>
</header>

<section class="card">
    <h2>ASSESSMENT SUMMARY</h2>

    <div class="metrics">
        <div class="metric">
            TOTAL
            <strong>{summary["total_checks"]}</strong>
        </div>

        <div class="metric">
            PASS
            <strong class="pass">{summary["pass"]}</strong>
        </div>

        <div class="metric">
            WARNING
            <strong class="warning">{summary["warning"]}</strong>
        </div>

        <div class="metric">
            ERROR
            <strong class="error">{summary["error"]}</strong>
        </div>

        <div class="metric">
            INFO
            <strong class="info">{summary["info"]}</strong>
        </div>
    </div>
</section>

<section class="card">
    <h2>ASSESSMENT DETAILS</h2>

    <p>
        <strong>Name:</strong>
        {html.escape(report_info["assessment_name"])}
    </p>

    <p>
        <strong>Assessment time:</strong>
        {html.escape(report_info["assessment_timestamp"])}
    </p>

    <table>
        <thead>
            <tr>
                <th>CHECK</th>
                <th>STATUS</th>
                <th>DETAILS</th>
            </tr>
        </thead>

        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
</section>

<section class="card">
    <h2>RECOMMENDATIONS</h2>
    <ul>
        {''.join(recommendation_items)}
    </ul>
</section>

<footer>
    NEMESIS CORE — AUTHORIZED LOCAL SECURITY RESEARCH
    <br>
    This report reflects the checks recorded at assessment time.
</footer>

</div>
</body>
</html>
"""

    output_path = (
        REPORTS_DIR / f"assessment_{record_id}.html"
    )

    with output_path.open("w", encoding="utf-8") as file:
        file.write(document)

    return output_path
