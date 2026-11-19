
// ==========================================
// NEMESIS CORE - DASHBOARD CONTROLLER 2.0
// ==========================================


// ==========================================
// SHARED HELPERS
// ==========================================

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = String(value ?? "N/A");
    }
}

async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("Invalid JSON response from server.");
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || `HTTP ${response.status}`);
    }

    return data;
}

function createHistoryItem(title, details = []) {
    const item = document.createElement("div");
    item.className = "recon-history-item";

    const heading = document.createElement("strong");
    heading.textContent = String(title ?? "N/A");
    item.appendChild(heading);

    details.forEach(detail => {
        const paragraph = document.createElement("p");
        paragraph.textContent = String(detail ?? "N/A");
        item.appendChild(paragraph);
    });

    return item;
}

function renderDistribution(container, distribution, emptyMessage) {
    if (!container) return;

    container.replaceChildren();

    if (
        !distribution ||
        typeof distribution !== "object" ||
        Object.keys(distribution).length === 0
    ) {
        container.textContent = emptyMessage;
        return;
    }

    Object.entries(distribution).forEach(([name, count]) => {
        container.appendChild(
            createHistoryItem(name, [`Count: ${count}`])
        );
    });
}


// ==========================================
// NAVIGATION
// ==========================================

const navigation = document.querySelectorAll(".nav-item");
const pages = document.querySelectorAll(".page");
const currentPage = document.getElementById("current-page");

function showPage(target) {
    navigation.forEach(item => {
        item.classList.toggle("active", item.dataset.page === target);
    });

    pages.forEach(page => {
        page.classList.toggle("active", page.id === target);
    });

    if (currentPage) {
        currentPage.textContent = target.replaceAll("-", " ").toUpperCase();
    }

    const loaders = {
        recon: loadReconHistory,
        assessment: loadAssessmentHistory,
        reports: loadReports,
        simulation: loadSimulationHistory,
        "threat-intelligence": loadThreatIntelligence,
        analytics: loadDetectionAnalytics,
        monitoring: loadSecurityMonitoring
    };

    if (loaders[target]) {
        loaders[target]();
    }
}

navigation.forEach(button => {
    button.addEventListener("click", () => {
        showPage(button.dataset.page);
    });
});

document.querySelectorAll(".module-link[data-target]").forEach(button => {
    button.addEventListener("click", () => {
        showPage(button.dataset.target);
    });
});


// ==========================================
// LOCAL CLOCK
// ==========================================

function updateClock() {
    const clock = document.getElementById("clock");

    if (clock) {
        clock.textContent = new Date().toLocaleTimeString(
            "en-GB",
            { hour12: false }
        );
    }
}

updateClock();
setInterval(updateClock, 1000);


// ==========================================
// SYSTEM STATUS
// ==========================================

async function loadSystemStatus() {
    try {
        const data = await fetchJSON("/api/status");

        setText(
            "platform",
            `${data.platform} ${data.platform_version}`
        );

        const sentinel = document.getElementById("sentinel-status");

        if (sentinel) {
            sentinel.textContent = data.sentinel_detected
                ? "DETECTED"
                : "NOT FOUND";

            sentinel.className = data.sentinel_detected
                ? "metric-value green"
                : "metric-value";
        }

        const integrationDetail = data.sentinel_detected
            ? "SENTINEL X directory detected. Integration is not configured yet."
            : "SENTINEL X directory was not detected.";

        setText("integration-detail", integrationDetail);
        setText("integration-page-detail", integrationDetail);
        setText("overview-assessment", data.assessment_count);

    } catch (error) {
        console.error("[NEMESIS] Status error:", error);
    }
}

loadSystemStatus();


// ==========================================
// RECONNAISSANCE CONTROLLER
// ==========================================

const reconButton = document.getElementById("run-recon");

async function runReconnaissance() {
    const message = document.getElementById("recon-message");

    if (!reconButton || !message) return;

    reconButton.disabled = true;
    reconButton.textContent = "SCANNING...";
    message.textContent = "Collecting local system inventory...";

    try {
        const data = await fetchJSON("/api/recon/run", {
            method: "POST"
        });

        const result = data.result;

        setText("recon-hostname", result.system.hostname);
        setText(
            "recon-os",
            `${result.system.operating_system} ${result.system.os_release}`
        );
        setText("recon-ip", result.network.local_ip);
        setText("recon-architecture", result.system.architecture);
        setText("overview-recon", "COMPLETE");

        message.textContent =
            `Reconnaissance completed. Record ID: ${data.record_id}`;

        await loadReconHistory();

    } catch (error) {
        message.textContent = `ERROR: ${error.message}`;
    } finally {
        reconButton.disabled = false;
        reconButton.textContent = "RUN RECON";
    }
}

if (reconButton) {
    reconButton.addEventListener("click", runReconnaissance);
}


// ==========================================
// RECONNAISSANCE HISTORY
// ==========================================

async function loadReconHistory() {
    const container = document.getElementById("recon-history");
    if (!container) return;

    try {
        const data = await fetchJSON("/api/recon/history");
        const records = data.records || [];

        if (records.length === 0) {
            container.textContent = "No reconnaissance records.";
            return;
        }

        container.replaceChildren();

        records.forEach(record => {
            container.appendChild(
                createHistoryItem(
                    `#${record.id} - ${record.hostname}`,
                    [record.timestamp]
                )
            );
        });

    } catch (error) {
        container.textContent = error.message;
    }
}


// ==========================================
// SECURITY ASSESSMENT
// ==========================================

const assessmentButton = document.getElementById("run-assessment");

function updateAssessmentSummary(checks) {
    let total = 0;
    let pass = 0;
    let warning = 0;
    let error = 0;

    Object.values(checks).forEach(check => {
        if (!check || typeof check !== "object") return;

        total++;

        const status = String(check.status || "").toUpperCase();

        if (status === "PASS") pass++;
        else if (status === "WARNING") warning++;
        else if (status === "ERROR" || status === "UNSUPPORTED") error++;
    });

    setText("assessment-total", total);
    setText("assessment-pass", pass);
    setText("assessment-warning", warning);
    setText("assessment-error", error);
}

function renderAssessmentResults(checks) {
    const container = document.getElementById("assessment-results");
    if (!container) return;

    container.replaceChildren();

    Object.entries(checks).forEach(([name, check]) => {
        const details = typeof check.details === "string"
            ? check.details
            : JSON.stringify(check.details, null, 2);

        container.appendChild(
            createHistoryItem(
                `${name.replaceAll("_", " ").toUpperCase()} - ${check.status}`,
                [details]
            )
        );
    });
}

async function runSecurityAssessment() {
    const message = document.getElementById("assessment-message");

    if (!assessmentButton || !message) return;

    assessmentButton.disabled = true;
    assessmentButton.textContent = "ASSESSING...";
    message.textContent = "Running read-only Windows security checks...";

    try {
        const data = await fetchJSON("/api/assessment/run", {
            method: "POST"
        });

        updateAssessmentSummary(data.result.checks);
        renderAssessmentResults(data.result.checks);

        message.textContent =
            `Assessment completed. Record ID: ${data.record_id}`;

        await loadAssessmentHistory();
        await loadSystemStatus();

    } catch (error) {
        message.textContent = `ERROR: ${error.message}`;
    } finally {
        assessmentButton.disabled = false;
        assessmentButton.textContent = "RUN ASSESSMENT";
    }
}

if (assessmentButton) {
    assessmentButton.addEventListener("click", runSecurityAssessment);
}


// ==========================================
// ASSESSMENT HISTORY
// ==========================================

async function loadAssessmentHistory() {
    const container = document.getElementById("assessment-history");
    if (!container) return;

    try {
        const data = await fetchJSON("/api/assessment/history");
        const records = data.records || [];

        if (records.length === 0) {
            container.textContent = "No assessment records.";
            return;
        }

        container.replaceChildren();

        records.forEach(record => {
            container.appendChild(
                createHistoryItem(
                    `#${record.id} - ${record.assessment}`,
                    [
                        record.timestamp,
                        `Total: ${record.total_checks} | PASS: ${record.pass_count} | WARNING: ${record.warning_count} | ERROR: ${record.error_count}`
                    ]
                )
            );
        });

    } catch (error) {
        container.textContent = error.message;
    }
}


// ==========================================
// REPORT CENTER
// ==========================================

const refreshReportsButton = document.getElementById("refresh-reports");

async function loadReports() {
    const container = document.getElementById("report-list");
    const message = document.getElementById("report-message");

    if (!container || !message) return;

    container.textContent = "Loading assessment reports...";
    message.textContent = "Retrieving saved assessment records...";

    try {
        const data = await fetchJSON("/api/assessment/history");
        const records = data.records || [];

        setText("report-total", data.total ?? records.length);
        setText(
            "report-latest",
            records.length > 0 ? `#${records[0].id}` : "---"
        );

        if (records.length === 0) {
            container.textContent = "No assessment reports available.";
            message.textContent = "Report center ready.";
            return;
        }

        container.replaceChildren();

        records.forEach(record => {
            const item = createHistoryItem(
                `REPORT #${record.id} - ${record.assessment}`,
                [
                    `Assessment time: ${record.timestamp}`,
                    `TOTAL: ${record.total_checks} | PASS: ${record.pass_count} | WARNING: ${record.warning_count} | ERROR: ${record.error_count}`
                ]
            );

            const actions = document.createElement("div");
            actions.className = "report-actions";

            const htmlButton = document.createElement("button");
            htmlButton.type = "button";
            htmlButton.className = "recon-button";
            htmlButton.textContent = "VIEW HTML REPORT";

            htmlButton.addEventListener("click", () => {
                const reportWindow = window.open(
                    `/api/reports/${record.id}/html`,
                    "_blank"
                );

                if (!reportWindow) {
                    message.textContent =
                        "Popup blocked. Allow popups for this local dashboard.";
                }
            });

            const jsonLink = document.createElement("a");
            jsonLink.className = "module-link";
            jsonLink.textContent = "DOWNLOAD JSON";
            jsonLink.href = `/api/reports/${record.id}/json`;

            actions.append(htmlButton, jsonLink);
            item.appendChild(actions);
            container.appendChild(item);
        });

        message.textContent =
            `${records.length} assessment report(s) loaded successfully.`;

    } catch (error) {
        container.textContent = `ERROR: ${error.message}`;
        message.textContent = "Report retrieval failed.";
    }
}

if (refreshReportsButton) {
    refreshReportsButton.addEventListener("click", loadReports);
}


// ==========================================
// SIMULATION LAB
// ==========================================

const simulationMessage = document.getElementById("simulation-message");
const simulationResult = document.getElementById("simulation-result");
const simulationButtons = document.querySelectorAll(".simulation-run");
const refreshSimulationButton = document.getElementById("refresh-simulation");

function renderSimulationResult(event, detection, recordId) {
    if (!simulationResult) return;

    simulationResult.replaceChildren();

    const fields = [
        ["SCENARIO", event.scenario_name],
        ["EVENT CODE", event.event_code],
        ["CATEGORY", event.category],
        ["SEVERITY", event.severity],
        ["EVENT STATUS", event.status],
        ["DETECTION STATUS", detection.status],
        ["DETECTION RULE", detection.matched_rule],
        ["RULE ID", detection.detection_id],
        ["RECORD ID", recordId],
        ["TIMESTAMP", event.timestamp],
        ["EXECUTION MODE", event.execution_mode]
    ];

    fields.forEach(([label, value]) => {
        simulationResult.appendChild(
            createHistoryItem(label, [value])
        );
    });

    const description = document.createElement("p");
    description.textContent = event.description || "";

    const recommendation = document.createElement("p");
    recommendation.textContent =
        `Recommendation: ${detection.recommendation || "N/A"}`;

    simulationResult.append(description, recommendation);
}

async function runSimulation(scenarioId, button) {
    if (!simulationMessage || !simulationResult) return;

    simulationButtons.forEach(item => {
        item.disabled = true;
    });

    const originalText = button.textContent;
    button.textContent = "GENERATING...";
    simulationMessage.textContent =
        `Generating inert event: ${scenarioId}...`;

    try {
        const data = await fetchJSON("/api/simulation/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ scenario_id: scenarioId })
        });

        renderSimulationResult(
            data.event,
            data.detection,
            data.record_id
        );

        simulationMessage.textContent =
            `Simulation completed. Record ID: ${data.record_id}. Detection: ${data.detection.status}.`;

        await loadSimulationHistory();

    } catch (error) {
        simulationMessage.textContent = `ERROR: ${error.message}`;
    } finally {
        simulationButtons.forEach(item => {
            item.disabled = false;
        });

        button.textContent = originalText;
    }
}

simulationButtons.forEach(button => {
    button.addEventListener("click", () => {
        const scenarioId = button.dataset.scenario;

        if (scenarioId) {
            runSimulation(scenarioId, button);
        }
    });
});


// ==========================================
// SIMULATION HISTORY
// ==========================================

async function loadSimulationHistory() {
    const container = document.getElementById("simulation-history");
    if (!container) return;

    try {
        const data = await fetchJSON("/api/simulation/history");
        const records = data.records || [];

        setText("simulation-total", data.total ?? records.length);

        const detectedCount = records.filter(record =>
            record.detection_status === "DETECTED"
        ).length;

        setText("simulation-detected", detectedCount);

        if (records.length === 0) {
            container.textContent = "No simulation records.";
            return;
        }

        container.replaceChildren();

        records.forEach(record => {
            container.appendChild(
                createHistoryItem(
                    `#${record.id} - ${record.scenario_name}`,
                    [
                        `EVENT: ${record.event_code} | SEVERITY: ${record.severity} | DETECTION: ${record.detection_status}`,
                        `Matched rule: ${record.matched_rule || "None"}`,
                        record.timestamp
                    ]
                )
            );
        });

    } catch (error) {
        container.textContent = `ERROR: ${error.message}`;
    }
}

if (refreshSimulationButton) {
    refreshSimulationButton.addEventListener("click", loadSimulationHistory);
}


// ==========================================
// THREAT INTELLIGENCE CONTROLLER
// ==========================================

const refreshThreatButton = document.getElementById("refresh-threat-intel");

async function loadThreatIntelligence() {
    const container = document.getElementById("threat-intel-list");
    const message = document.getElementById("threat-intel-message");

    if (!container) return;

    container.textContent = "Loading threat intelligence catalog...";

    try {
        const data = await fetchJSON("/api/threat-intelligence/catalog");
        const summary = data.summary || {};
        const threats = data.threats || {};

        setText("threat-version", summary.catalog_version);
        setText("threat-total", summary.total_entries);
        setText("threat-mappings", summary.mitre_mappings);
        setText("threat-status", summary.mapping_status);

        container.replaceChildren();

        Object.entries(threats).forEach(([scenarioId, threat]) => {
            const mitre = threat.mitre || {};

            const item = document.createElement("div");
            item.className = "recon-history-item";

            const heading = document.createElement("strong");
            heading.textContent = threat.title || threat.scenario_name || scenarioId;

            const description = document.createElement("p");
            description.textContent = threat.description || "";

            const mapping = document.createElement("p");
            mapping.textContent =
                `Scenario: ${scenarioId} | Event: ${threat.event_code || "N/A"} | Severity: ${threat.severity || "N/A"}`;

            const technique = document.createElement("p");
            technique.textContent =
                `MITRE candidate: ${mitre.technique_id || "N/A"} - ${mitre.technique_name || "N/A"}`;

            const tactic = document.createElement("p");
            tactic.textContent =
                `Tactic: ${mitre.tactic || "N/A"} | Confidence: ${mitre.confidence || "N/A"} | Status: ${mitre.mapping_status || "N/A"}`;

            const evidence = document.createElement("p");
            evidence.textContent =
                `Evidence required: ${mitre.evidence_required || "N/A"}`;

            item.append(
                heading,
                description,
                mapping,
                technique,
                tactic,
                evidence
            );

            if (Array.isArray(threat.defensive_guidance)) {
                const guidance = document.createElement("p");
                guidance.textContent =
                    `Defensive guidance: ${threat.defensive_guidance.join(" ")}`;
                item.appendChild(guidance);
            }

            container.appendChild(item);
        });

        if (message) {
            message.textContent =
                `${Object.keys(threats).length} catalog entries loaded. MITRE references are candidate mappings only.`;
        }

    } catch (error) {
        container.textContent = `ERROR: ${error.message}`;

        if (message) {
            message.textContent = "Threat intelligence retrieval failed.";
        }
    }
}

if (refreshThreatButton) {
    refreshThreatButton.addEventListener("click", loadThreatIntelligence);
}


// ==========================================
// DETECTION ANALYTICS CONTROLLER
// ==========================================

const refreshAnalyticsButton = document.getElementById("refresh-analytics");

async function loadDetectionAnalytics() {
    const message = document.getElementById("analytics-message");

    try {
        const data = await fetchJSON("/api/analytics/summary");

        setText("analytics-total", data.total_records);
        setText("analytics-detected", data.detected_events);
        setText("analytics-not-detected", data.not_detected_events);
        setText(
            "analytics-coverage",
            `${Number(data.detection_coverage_percent ?? 0).toFixed(1)}%`
        );

        if (message) {
            message.textContent =
                `${data.analysis_mode || "READ_ONLY_SIMULATION_ANALYTICS"} — stored inert simulation events only.`;
        }

        // The summary endpoint provides counts only.
        // Distribution panels are populated from monitoring summary.
        const monitoring = await fetchJSON("/api/monitoring/summary");

        renderDistribution(
            document.getElementById("analytics-scenarios"),
            monitoring.scenario_distribution,
            "No scenario data."
        );

        renderDistribution(
            document.getElementById("analytics-severity"),
            monitoring.severity_distribution,
            "No severity data."
        );

        renderDistribution(
            document.getElementById("analytics-categories"),
            monitoring.detection_distribution,
            "No detection distribution data."
        );

    } catch (error) {
        if (message) {
            message.textContent = `ERROR: ${error.message}`;
        }

        console.error("[NEMESIS] Analytics error:", error);
    }
}

if (refreshAnalyticsButton) {
    refreshAnalyticsButton.addEventListener("click", loadDetectionAnalytics);
}


// ==========================================
// SECURITY MONITORING CONTROLLER
// ==========================================

const refreshMonitoringButton = document.getElementById("refresh-monitoring");

async function loadSecurityMonitoring() {
    const container = document.getElementById("monitoring-timeline");
    const message = document.getElementById("monitoring-message");

    if (!container) return;

    container.textContent = "Loading monitoring timeline...";

    try {
        const [timeline, summary] = await Promise.all([
            fetchJSON("/api/monitoring/timeline"),
            fetchJSON("/api/monitoring/summary")
        ]);

        setText("monitoring-total", summary.total_records);
        setText("monitoring-detected", summary.detected_events);
        setText("monitoring-not-detected", summary.not_detected_events);
        setText("monitoring-mode", summary.monitoring_mode);

        const events = timeline.events || [];

        if (events.length === 0) {
            container.textContent = "No monitoring events available.";
        } else {
            container.replaceChildren();

            events.forEach(event => {
                container.appendChild(
                    createHistoryItem(
                        `#${event.record_id} - ${event.scenario_name}`,
                        [
                            `Event: ${event.event_code} | Severity: ${event.severity}`,
                            `Detection: ${event.detection_status}`,
                            `Matched rule: ${event.matched_rule || "None"}`,
                            `Source: ${event.source || "N/A"}`,
                            `Timestamp: ${event.timestamp}`
                        ]
                    )
                );
            });
        }

        if (message) {
            message.textContent =
                summary.interpretation ||
                "Read-only timeline of inert local simulation events.";
        }

    } catch (error) {
        container.textContent = `ERROR: ${error.message}`;

        if (message) {
            message.textContent = "Monitoring retrieval failed.";
        }
    }
}

if (refreshMonitoringButton) {
    refreshMonitoringButton.addEventListener("click", loadSecurityMonitoring);
}


// ==========================================
// INITIALIZATION
// ==========================================

console.log("[NEMESIS] Dashboard controller initialized.");

loadSystemStatus();
