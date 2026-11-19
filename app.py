
from pathlib import Path
from flask import Flask, render_template, jsonify, send_file, request
from datetime import datetime
import platform

from config import (
    APP_NAME,
    APP_VERSION,
    SENTINEL_PATH,
    REPORTS_DIR,
)

from modules.reconnaissance import run_reconnaissance
from modules.recon_database import (
    initialize_database as initialize_recon_database,
    save_reconnaissance,
    get_reconnaissance_history
)

from modules.assessment.security_checks import run_security_assessment
from modules.assessment.assessment_database import (
    initialize_database as initialize_assessment_database,
    save_assessment,
    get_assessment_history,
    get_assessment_count
)

from modules.assessment.report_generator import (
    generate_json_report,
    generate_html_report
)

from modules.simulation.simulation_engine import (
    get_available_scenarios,
    run_simulation
)

from modules.simulation.detection_engine import analyze_event

from modules.simulation.simulation_database import (
    initialize_simulation_database,
    save_simulation,
    get_simulation_history,
    get_simulation_count
)

from modules.detection_analytics.analytics_engine import (
    analyze_detection_coverage,
    get_analytics_summary
)

from modules.threat_intelligence.catalog import (
    get_all_threats,
    get_threat_by_scenario,
    get_catalog_summary
)

from modules.monitoring.monitoring_engine import (
    get_monitoring_timeline,
    get_monitoring_summary
)

from modules.unified_reporting.report_engine import (
    generate_unified_report
)

from modules.unified_reporting.export_generator import (
    generate_unified_json_export,
    generate_unified_html_export,
    list_unified_exports,
    EXPORT_PREFIX,
)


app = Flask(__name__)

initialize_recon_database()
initialize_assessment_database()
initialize_simulation_database()


@app.route("/")
def dashboard():
    return render_template(
        "index.html",
        app_name=APP_NAME,
        version=APP_VERSION
    )


@app.route("/api/status")
def system_status():

    try:
        assessment_count = get_assessment_count()
    except Exception:
        app.logger.exception("Could not retrieve assessment count")
        assessment_count = 0

    return jsonify({
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "ONLINE",
        "platform": platform.system(),
        "platform_version": platform.release(),
        "sentinel_detected": SENTINEL_PATH.exists(),
        "assessment_count": assessment_count,
        "timestamp": datetime.now().isoformat()
    })


# ==========================================
# RECONNAISSANCE API
# ==========================================

@app.route("/api/recon/run", methods=["POST"])
def recon_run():

    try:
        result = run_reconnaissance()
        record_id = save_reconnaissance(result)

        return jsonify({
            "success": True,
            "record_id": record_id,
            "result": result
        })

    except Exception:
        app.logger.exception("Reconnaissance failed")

        return jsonify({
            "success": False,
            "error": "Reconnaissance could not be completed."
        }), 500


@app.route("/api/recon/history")
def recon_history():

    try:
        records = get_reconnaissance_history()

        return jsonify({
            "success": True,
            "total": len(records),
            "records": records[:20]
        })

    except Exception:
        app.logger.exception("History retrieval failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve reconnaissance history."
        }), 500


# ==========================================
# SECURITY ASSESSMENT API
# ==========================================

@app.route("/api/assessment/run", methods=["POST"])
def assessment_run():

    try:
        result = run_security_assessment()
        record_id = save_assessment(result)

        return jsonify({
            "success": True,
            "record_id": record_id,
            "result": result
        })

    except Exception:
        app.logger.exception("Security assessment failed")

        return jsonify({
            "success": False,
            "error": "Security assessment could not be completed."
        }), 500


@app.route("/api/assessment/history")
def assessment_history():

    try:
        records = get_assessment_history(limit=20)

        return jsonify({
            "success": True,
            "total": get_assessment_count(),
            "records": records
        })

    except Exception:
        app.logger.exception("Assessment history retrieval failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve assessment history."
        }), 500


# ==========================================
# ASSESSMENT REPORT API
# ==========================================

@app.route("/api/reports/<int:record_id>/json")
def assessment_json_report(record_id):

    try:
        report_path = generate_json_report(record_id)

        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"assessment_{record_id}.json",
            mimetype="application/json"
        )

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Assessment record not found."
        }), 404

    except Exception:
        app.logger.exception("JSON report generation failed")

        return jsonify({
            "success": False,
            "error": "Could not generate JSON report."
        }), 500


@app.route("/api/reports/<int:record_id>/html")
def assessment_html_report(record_id):

    try:
        report_path = generate_html_report(record_id)

        return send_file(
            report_path,
            as_attachment=False,
            mimetype="text/html"
        )

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Assessment record not found."
        }), 404

    except Exception:
        app.logger.exception("HTML report generation failed")

        return jsonify({
            "success": False,
            "error": "Could not generate HTML report."
        }), 500


# ==========================================
# UNIFIED SECURITY REPORT API
# ==========================================

@app.route("/api/reports/unified", methods=["GET"])
def unified_security_report():

    try:
        report = generate_unified_report()

        return jsonify(report)

    except Exception:
        app.logger.exception("Unified report generation failed")

        return jsonify({
            "success": False,
            "error": "Could not generate unified security report."
        }), 500


# ==========================================
# UNIFIED REPORT EXPORT API
# ==========================================

@app.route(
    "/api/reports/unified/export/json",
    methods=["GET"]
)
def export_unified_json():

    try:
        report_path = generate_unified_json_export()

        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_path.name,
            mimetype="application/json"
        )

    except Exception:
        app.logger.exception("Unified JSON export failed")

        return jsonify({
            "success": False,
            "error": "Could not export unified JSON report."
        }), 500


@app.route(
    "/api/reports/unified/export/html",
    methods=["GET"]
)
def export_unified_html():

    try:
        report_path = generate_unified_html_export()

        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_path.name,
            mimetype="text/html"
        )

    except Exception:
        app.logger.exception("Unified HTML export failed")

        return jsonify({
            "success": False,
            "error": "Could not export unified HTML report."
        }), 500


@app.route(
    "/api/reports/unified/exports",
    methods=["GET"]
)
def unified_export_history():

    try:
        limit = request.args.get("limit", default=50, type=int)

        if limit is None:
            limit = 50

        exports = list_unified_exports(limit=limit)

        return jsonify({
            "success": True,
            "total": len(exports),
            "exports": exports
        })

    except Exception:
        app.logger.exception("Unified export history failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve export history."
        }), 500


@app.route(
    "/api/reports/unified/download/<string:filename>",
    methods=["GET"]
)
def download_unified_export(filename):

    try:
        # Accept only generated NEMESIS export filenames.
        if (
            not filename.startswith(EXPORT_PREFIX)
            or Path(filename).name != filename
            or Path(filename).suffix.lower() not in {".json", ".html"}
        ):
            return jsonify({
                "success": False,
                "error": "Invalid export filename."
            }), 400

        export_directory = REPORTS_DIR.resolve()
        export_path = (export_directory / filename).resolve()

        # Prevent path traversal and access outside reports/.
        if export_path.parent != export_directory:
            return jsonify({
                "success": False,
                "error": "Invalid export path."
            }), 400

        if not export_path.is_file():
            return jsonify({
                "success": False,
                "error": "Export file not found."
            }), 404

        mimetype = (
            "application/json"
            if export_path.suffix.lower() == ".json"
            else "text/html"
        )

        return send_file(
            export_path,
            as_attachment=True,
            download_name=export_path.name,
            mimetype=mimetype
        )

    except Exception:
        app.logger.exception("Unified export download failed")

        return jsonify({
            "success": False,
            "error": "Could not download export file."
        }), 500


# ==========================================
# SIMULATION API
# ==========================================

@app.route("/api/simulation/scenarios", methods=["GET"])
def simulation_scenarios():

    try:
        scenarios = get_available_scenarios()

        return jsonify({
            "success": True,
            "total": len(scenarios),
            "scenarios": scenarios
        })

    except Exception:
        app.logger.exception("Scenario retrieval failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve simulation scenarios."
        }), 500


@app.route("/api/simulation/run", methods=["POST"])
def simulation_run():

    try:
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({
                "success": False,
                "error": "A JSON request body is required."
            }), 400

        scenario_id = payload.get("scenario_id")

        if not isinstance(scenario_id, str):
            return jsonify({
                "success": False,
                "error": "A valid scenario_id is required."
            }), 400

        event = run_simulation(scenario_id)
        detection = analyze_event(event)

        record_id = save_simulation(event, detection)

        return jsonify({
            "success": True,
            "record_id": record_id,
            "event": event,
            "detection": detection
        })

    except ValueError as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 400

    except Exception:
        app.logger.exception("Simulation execution failed")

        return jsonify({
            "success": False,
            "error": "Simulation could not be completed."
        }), 500


@app.route("/api/simulation/history", methods=["GET"])
def simulation_history():

    try:
        records = get_simulation_history(limit=20)
        total = get_simulation_count()

        return jsonify({
            "success": True,
            "total": total,
            "records": records
        })

    except Exception:
        app.logger.exception("Simulation history retrieval failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve simulation history."
        }), 500


# ==========================================
# DETECTION ANALYTICS API
# ==========================================

@app.route("/api/analytics/summary", methods=["GET"])
def analytics_summary():

    try:
        result = get_analytics_summary()

        return jsonify(result)

    except Exception:
        app.logger.exception("Analytics summary failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve analytics summary."
        }), 500


@app.route("/api/analytics/coverage", methods=["GET"])
def analytics_coverage():

    try:
        result = analyze_detection_coverage()

        return jsonify({
            "success": True,
            "analytics": result
        })

    except Exception:
        app.logger.exception("Detection coverage analysis failed")

        return jsonify({
            "success": False,
            "error": "Could not analyze detection coverage."
        }), 500


# ==========================================
# THREAT INTELLIGENCE API
# ==========================================

@app.route("/api/threat-intelligence/catalog", methods=["GET"])
def threat_intelligence_catalog():

    try:
        threats = get_all_threats()
        summary = get_catalog_summary()

        return jsonify({
            "success": True,
            "summary": summary,
            "total": len(threats),
            "threats": threats
        })

    except Exception:
        app.logger.exception("Threat catalog retrieval failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve threat intelligence catalog."
        }), 500


@app.route(
    "/api/threat-intelligence/<string:scenario_id>",
    methods=["GET"]
)
def threat_intelligence_detail(scenario_id):

    try:
        threat = get_threat_by_scenario(scenario_id)

        if threat is None:
            return jsonify({
                "success": False,
                "error": "Threat mapping not found."
            }), 404

        return jsonify({
            "success": True,
            "threat": threat
        })

    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid scenario identifier."
        }), 400

    except Exception:
        app.logger.exception("Threat intelligence lookup failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve threat intelligence."
        }), 500


# ==========================================
# SECURITY MONITORING API
# ==========================================

@app.route("/api/monitoring/timeline", methods=["GET"])
def monitoring_timeline():

    try:
        limit = request.args.get("limit", default=50)

        result = get_monitoring_timeline(limit=limit)

        return jsonify(result)

    except Exception:
        app.logger.exception("Monitoring timeline failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve monitoring timeline."
        }), 500


@app.route("/api/monitoring/summary", methods=["GET"])
def monitoring_summary():

    try:
        result = get_monitoring_summary()

        return jsonify(result)

    except Exception:
        app.logger.exception("Monitoring summary failed")

        return jsonify({
            "success": False,
            "error": "Could not retrieve monitoring summary."
        }), 500


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    print("=" * 50)
    print("          N E M E S I S DASHBOARD")
    print("=" * 50)
    print("[ONLINE] NEMESIS Web Server")
    print("[LOCAL] http://127.0.0.1:8765")
    print("[INFO] Press CTRL+C to stop")

    app.run(
        host="127.0.0.1",
        port=8765,
        debug=False
    )
