
// ==========================================
// NEMESIS CORE
// EXECUTIVE DASHBOARD CONTROLLER
// STAGE 9.4
// ==========================================

(() => {
    "use strict";

    const API_URL = "/api/reports/unified";

    function createElement(tag, className, text) {
        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        if (text !== undefined && text !== null) {
            element.textContent = String(text);
        }

        return element;
    }

    function createMetric(label, value, detail, valueClass = "") {
        const card = createElement("div", "metric-card");

        card.appendChild(
            createElement("span", "metric-label", label)
        );

        card.appendChild(
            createElement(
                "strong",
                `metric-value ${valueClass}`.trim(),
                value
            )
        );

        card.appendChild(
            createElement("span", "metric-detail", detail)
        );

        return card;
    }

    function createHistoryItem(title, details = []) {
        const item = createElement("div", "recon-history-item");

        item.appendChild(
            createElement("strong", "", title)
        );

        details.forEach(detail => {
            item.appendChild(
                createElement("p", "", detail)
            );
        });

        return item;
    }

    function createDashboard() {
        const overview = document.getElementById("overview");

        if (!overview) {
            return null;
        }

        const existing = document.getElementById(
            "executive-dashboard"
        );

        if (existing) {
            return existing;
        }

        const dashboard = createElement(
            "div",
            "",
        );

        dashboard.id = "executive-dashboard";

        const heading = createElement(
            "div",
            "page-heading"
        );

        const headingContent = createElement("div");

        headingContent.appendChild(
            createElement(
                "span",
                "eyebrow",
                "INTELLIGENCE OVERVIEW"
            )
        );

        headingContent.appendChild(
            createElement(
                "h2",
                "",
                "EXECUTIVE DASHBOARD"
            )
        );

        headingContent.appendChild(
            createElement(
                "p",
                "",
                "Unified summary of local assessments and inert simulations."
            )
        );

        const refreshButton = createElement(
            "button",
            "recon-button",
            "REFRESH EXECUTIVE DATA"
        );

        refreshButton.id = "refresh-executive";

        heading.append(
            headingContent,
            refreshButton
        );

        dashboard.appendChild(heading);

        const message = createElement(
            "div",
            "recon-message",
            "Executive dashboard standing by."
        );

        message.id = "executive-message";
        dashboard.appendChild(message);

        dashboard.appendChild(
            createElement(
                "div",
                "section-heading",
                "UNIFIED SECURITY SUMMARY"
            )
        );

        const metrics = createElement(
            "div",
            "metrics-grid"
        );

        metrics.id = "executive-metrics";

        dashboard.appendChild(metrics);

        const coveragePanel = createElement(
            "div",
            "panel recon-panel"
        );

        coveragePanel.appendChild(
            createElement(
                "h3",
                "",
                "DETECTION COVERAGE"
            )
        );

        const coverageValue = createElement(
            "strong",
            "metric-value green",
            "0%"
        );

        coverageValue.id = "executive-coverage";

        coveragePanel.appendChild(coverageValue);

        coveragePanel.appendChild(
            createElement(
                "p",
                "",
                "Coverage is calculated only from stored inert simulation records."
            )
        );

        dashboard.appendChild(coveragePanel);

        const scenarioPanel = createElement(
            "div",
            "panel recon-panel"
        );

        scenarioPanel.appendChild(
            createElement(
                "h3",
                "",
                "SCENARIO PERFORMANCE"
            )
        );

        const scenarioList = createElement("div");
        scenarioList.id = "executive-scenarios";

        scenarioPanel.appendChild(scenarioList);
        dashboard.appendChild(scenarioPanel);

        const scopePanel = createElement(
            "div",
            "panel recon-panel"
        );

        scopePanel.appendChild(
            createElement(
                "h3",
                "",
                "REPORT SCOPE & LIMITATIONS"
            )
        );

        const limitations = createElement("div");
        limitations.id = "executive-limitations";

        scopePanel.appendChild(limitations);
        dashboard.appendChild(scopePanel);

        // Insert immediately after the Overview hero.
        const hero = overview.querySelector(".hero");

        if (hero && hero.nextSibling) {
            overview.insertBefore(
                dashboard,
                hero.nextSibling
            );
        } else {
            overview.appendChild(dashboard);
        }

        refreshButton.addEventListener(
            "click",
            loadExecutiveDashboard
        );

        return dashboard;
    }

    async function loadExecutiveDashboard() {
        const dashboard = createDashboard();

        if (!dashboard) {
            return;
        }

        const message = document.getElementById(
            "executive-message"
        );

        const refreshButton = document.getElementById(
            "refresh-executive"
        );

        const metrics = document.getElementById(
            "executive-metrics"
        );

        if (refreshButton) {
            refreshButton.disabled = true;
            refreshButton.textContent = "LOADING...";
        }

        if (message) {
            message.textContent =
                "Retrieving unified security report...";
        }

        try {
            const response = await fetch(API_URL);

            let data;

            try {
                data = await response.json();
            } catch {
                throw new Error("Invalid JSON response.");
            }

            if (!response.ok || data.success === false) {
                throw new Error(
                    data.error || `HTTP ${response.status}`
                );
            }

            const summary = data.summary || {};
            const analytics = data.analytics || {};

            const assessmentCount =
                summary.assessment_records ?? 0;

            const simulationCount =
                summary.simulation_records ?? 0;

            const detectedCount =
                summary.detected_events ?? 0;

            const notDetectedCount =
                summary.not_detected_events ?? 0;

            const mappingCount =
                analytics.unique_mitre_mapping_count ?? 0;

            const coverage =
                Number(
                    summary.detection_coverage_percent ?? 0
                );

            if (metrics) {
                metrics.replaceChildren();

                metrics.append(
                    createMetric(
                        "ASSESSMENT RECORDS",
                        assessmentCount,
                        "Saved local assessments"
                    ),
                    createMetric(
                        "SIMULATION EVENTS",
                        simulationCount,
                        "Stored inert events"
                    ),
                    createMetric(
                        "DETECTED EVENTS",
                        detectedCount,
                        "Matched simulation rules",
                        "green"
                    ),
                    createMetric(
                        "NOT DETECTED",
                        notDetectedCount,
                        "Unmatched simulation events"
                    ),
                    createMetric(
                        "MITRE CANDIDATES",
                        mappingCount,
                        "Unique candidate references"
                    )
                );
            }

            const coverageElement = document.getElementById(
                "executive-coverage"
            );

            if (coverageElement) {
                coverageElement.textContent =
                    `${coverage.toFixed(2)}%`;
            }

            // Scenario statistics
            const scenarioContainer =
                document.getElementById(
                    "executive-scenarios"
                );

            if (scenarioContainer) {
                scenarioContainer.replaceChildren();

                const scenarioStats =
                    analytics.scenario_detection_stats || {};

                const entries = Object.entries(scenarioStats);

                if (entries.length === 0) {
                    scenarioContainer.textContent =
                        "No scenario statistics available.";
                } else {
                    entries.forEach(([scenario, stats]) => {
                        scenarioContainer.appendChild(
                            createHistoryItem(
                                scenario.replaceAll("_", " ").toUpperCase(),
                                [
                                    `Total: ${stats.total ?? 0}`,
                                    `Detected: ${stats.detected ?? 0}`,
                                    `Not detected: ${stats.not_detected ?? 0}`,
                                    `Ignored: ${stats.ignored ?? 0}`
                                ]
                            )
                        );
                    });
                }
            }

            // Report limitations
            const limitationsContainer =
                document.getElementById(
                    "executive-limitations"
                );

            if (limitationsContainer) {
                limitationsContainer.replaceChildren();

                const limitations = Array.isArray(data.limitations)
                    ? data.limitations
                    : [];

                if (limitations.length === 0) {
                    limitationsContainer.textContent =
                        "No limitation details provided.";
                } else {
                    limitations.forEach(item => {
                        limitationsContainer.appendChild(
                            createElement("p", "", `• ${item}`)
                        );
                    });
                }
            }

            if (message) {
                message.textContent =
                    `Unified report loaded successfully. Generated: ${data.generated_at || "N/A"}`;
            }

            console.log(
                "[NEMESIS] Executive dashboard updated."
            );

        } catch (error) {
            if (message) {
                message.textContent =
                    `ERROR: ${error.message}`;
            }

            console.error(
                "[NEMESIS] Executive dashboard error:",
                error
            );

        } finally {
            if (refreshButton) {
                refreshButton.disabled = false;
                refreshButton.textContent =
                    "REFRESH EXECUTIVE DATA";
            }
        }
    }

    // Initialize after the existing dashboard controller.
    createDashboard();
    loadExecutiveDashboard();

})();
