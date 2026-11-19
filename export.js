
/*
 * NEMESIS CORE
 * Export Center Controller
 *
 * Generates and downloads unified JSON/HTML reports.
 * Displays export history from the local Flask API.
 */

(() => {
    "use strict";

    const API = {
        history: "/api/reports/unified/exports",
        json: "/api/reports/unified/export/json",
        html: "/api/reports/unified/export/html"
    };

    const $ = (selector, root = document) =>
        root.querySelector(selector);

    function createElement(tag, className, text) {
        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        if (text !== undefined) {
            element.textContent = String(text);
        }

        return element;
    }

    function createDashboard() {
        const navigation = $(".navigation");
        const main = $(".main-content");

        if (!navigation || !main) {
            console.error("[NEMESIS] Export Center: dashboard structure missing.");
            return false;
        }

        if ($("#export-center")) {
            return true;
        }

        // Add navigation item.
        const navButton = createElement(
            "button",
            "nav-item",
            "EXPORT CENTER"
        );

        navButton.type = "button";
        navButton.dataset.page = "export-center";
        navigation.appendChild(navButton);

        // Create Export Center page.
        const page = createElement("section", "page");
        page.id = "export-center";

        const heading = createElement("div", "page-heading");
        const headingContent = document.createElement("div");

        headingContent.appendChild(
            createElement("span", "eyebrow", "UNIFIED REPORTING MODULE")
        );

        headingContent.appendChild(
            createElement("h2", "", "EXPORT CENTER")
        );

        headingContent.appendChild(
            createElement(
                "p",
                "",
                "Generate, download and manage local unified security reports."
            )
        );

        heading.appendChild(headingContent);
        page.appendChild(heading);

        // Export actions.
        const actions = createElement("div", "export-actions");

        const jsonButton = createElement(
            "button",
            "recon-button",
            "GENERATE JSON"
        );
        jsonButton.id = "export-json";
        jsonButton.type = "button";

        const htmlButton = createElement(
            "button",
            "recon-button",
            "GENERATE HTML"
        );
        htmlButton.id = "export-html";
        htmlButton.type = "button";

        const refreshButton = createElement(
            "button",
            "recon-button",
            "REFRESH HISTORY"
        );
        refreshButton.id = "refresh-exports";
        refreshButton.type = "button";

        actions.append(jsonButton, htmlButton, refreshButton);
        page.appendChild(actions);

        // Status message.
        const message = createElement(
            "div",
            "recon-message",
            "Export Center standing by."
        );
        message.id = "export-message";
        page.appendChild(message);

        // Metrics.
        const metrics = createElement("div", "metrics-grid");

        const totalCard = createElement("div", "metric-card");
        totalCard.appendChild(
            createElement("span", "metric-label", "TOTAL EXPORTS")
        );
        totalCard.appendChild(
            createElement("strong", "metric-value", "0")
        );
        totalCard.querySelector("strong").id = "export-total";

        totalCard.appendChild(
            createElement("span", "metric-detail", "Saved JSON and HTML files")
        );

        const latestCard = createElement("div", "metric-card");
        latestCard.appendChild(
            createElement("span", "metric-label", "LATEST FORMAT")
        );
        latestCard.appendChild(
            createElement("strong", "metric-value", "---")
        );
        latestCard.querySelector("strong").id = "export-latest";

        latestCard.appendChild(
            createElement("span", "metric-detail", "Most recent export")
        );

        metrics.append(totalCard, latestCard);
        page.appendChild(metrics);

        // Export history.
        const panel = createElement("div", "panel recon-panel");

        panel.appendChild(
            createElement("h3", "", "UNIFIED EXPORT HISTORY")
        );

        const history = createElement(
            "div",
            "export-history",
            "Loading export history..."
        );
        history.id = "export-history";

        panel.appendChild(history);
        page.appendChild(panel);

        // Scope and privacy notice.
        const notice = createElement(
            "p",
            "module-status",
            "SCOPE: LOCAL READ-ONLY CHECKS AND INERT SIMULATION RECORDS. " +
            "KEEP EXPORTED FILES PRIVATE."
        );

        page.appendChild(notice);

        const footer = $(".footer", main);

        if (footer) {
            main.insertBefore(page, footer);
        } else {
            main.appendChild(page);
        }

        // Dynamic styles.
        const style = document.createElement("style");

        style.textContent = `
            .export-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin: 20px 0;
            }

            .export-history {
                display: grid;
                gap: 12px;
            }

            .export-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 14px;
                padding: 16px;
                background: rgba(10, 16, 25, 0.85);
                border: 1px solid rgba(0, 230, 118, 0.18);
                border-radius: 6px;
            }

            .export-item-info {
                display: grid;
                gap: 6px;
                min-width: 180px;
            }

            .export-item-name {
                color: #e8edf5;
                font-weight: 600;
                overflow-wrap: anywhere;
            }

            .export-item-meta {
                color: #a0aabd;
                font-size: 12px;
            }

            .export-download {
                color: #00e676;
                text-decoration: none;
                font-weight: 700;
                border: 1px solid rgba(0, 230, 118, 0.35);
                padding: 9px 14px;
                border-radius: 4px;
            }

            .export-download:hover {
                background: rgba(0, 230, 118, 0.1);
            }

            .export-empty {
                padding: 18px;
                color: #a0aabd;
                text-align: center;
            }

            .export-actions button:disabled {
                opacity: 0.55;
                cursor: wait;
            }
        `;

        document.head.appendChild(style);

        return true;
    }

    function setMessage(message) {
        const element = $("#export-message");

        if (element) {
            element.textContent = message;
        }
    }

    function formatSize(bytes) {
        const size = Number(bytes);

        if (!Number.isFinite(size) || size < 0) {
            return "Unknown size";
        }

        if (size < 1024) {
            return `${size} B`;
        }

        if (size < 1024 * 1024) {
            return `${(size / 1024).toFixed(2)} KB`;
        }

        return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    }

    function formatDate(value) {
        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "Unknown date";
        }

        return date.toLocaleString();
    }

    async function loadExportHistory() {
        const container = $("#export-history");

        if (!container) {
            return;
        }

        container.textContent = "Loading export history...";

        try {
            const response = await fetch(API.history, {
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (!data.success || !Array.isArray(data.exports)) {
                throw new Error("Invalid export history response.");
            }

            const exports = data.exports;

            $("#export-total").textContent = String(exports.length);

            $("#export-latest").textContent =
                exports.length > 0
                    ? String(exports[0].format || "---")
                    : "---";

            container.replaceChildren();

            if (exports.length === 0) {
                container.appendChild(
                    createElement(
                        "div",
                        "export-empty",
                        "No unified exports found. Generate your first report."
                    )
                );

                return;
            }

            exports.forEach((item) => {
                if (!item || typeof item !== "object") {
                    return;
                }

                const row = createElement("div", "export-item");
                const info = createElement("div", "export-item-info");

                info.appendChild(
                    createElement(
                        "div",
                        "export-item-name",
                        item.name || "Unnamed export"
                    )
                );

                info.appendChild(
                    createElement(
                        "div",
                        "export-item-meta",
                        `${item.format || "UNKNOWN"} | ${formatSize(item.size_bytes)}`
                    )
                );

                info.appendChild(
                    createElement(
                        "div",
                        "export-item-meta",
                        `Created: ${formatDate(item.modified_at)}`
                    )
                );

                row.appendChild(info);

                const downloadUrl = item.download_url;

                if (
                    typeof downloadUrl === "string" &&
                    downloadUrl.startsWith(
                        "/api/reports/unified/download/"
                    )
                ) {
                    const link = createElement(
                        "a",
                        "export-download",
                        "DOWNLOAD"
                    );

                    link.href = downloadUrl;
                    link.setAttribute("download", "");
                    row.appendChild(link);
                }

                container.appendChild(row);
            });

            setMessage(`Export history loaded. ${exports.length} file(s) available.`);
        } catch (error) {
            console.error("[NEMESIS] Export history error:", error);

            container.textContent = "Could not load export history.";
            setMessage("ERROR: Could not load export history.");
        }
    }

    async function generateExport(format) {
        const endpoint = format === "JSON" ? API.json : API.html;

        const button = $(
            format === "JSON" ? "#export-json" : "#export-html"
        );

        if (!button) {
            return;
        }

        button.disabled = true;
        setMessage(`Generating ${format} export...`);

        try {
            const response = await fetch(endpoint, {
                method: "GET",
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const blob = await response.blob();

            if (blob.size === 0) {
                throw new Error("The generated export is empty.");
            }

            const disposition =
                response.headers.get("Content-Disposition") || "";

            const match = disposition.match(
                /filename="?([^";]+)"?/i
            );

            const filename = match
                ? match[1]
                : `nemesis_unified_export.${format.toLowerCase()}`;

            const objectUrl = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = objectUrl;
            link.download = filename;

            document.body.appendChild(link);
            link.click();
            link.remove();

            window.setTimeout(() => {
                URL.revokeObjectURL(objectUrl);
            }, 1000);

            setMessage(`${format} export generated. Download started.`);

            await loadExportHistory();
        } catch (error) {
            console.error("[NEMESIS] Export generation error:", error);
            setMessage(`ERROR: ${format} export could not be generated.`);
        } finally {
            button.disabled = false;
        }
    }

    function initializeNavigation() {
        const navigation = $(".navigation");

        if (!navigation) {
            return;
        }

        /*
         * Capture navigation clicks so the dynamically created
         * Export Center page works with the existing navigation.
         */
        navigation.addEventListener(
            "click",
            (event) => {
                const button = event.target.closest(".nav-item");

                if (!button || !navigation.contains(button)) {
                    return;
                }

                const pageId = button.dataset.page;
                const target = document.getElementById(pageId);

                if (!target) {
                    return;
                }

                document.querySelectorAll(".nav-item").forEach((item) => {
                    item.classList.toggle("active", item === button);
                });

                document.querySelectorAll(".page").forEach((page) => {
                    page.classList.toggle("active", page.id === pageId);
                });

                const currentPage = $("#current-page");

                if (currentPage) {
                    currentPage.textContent = button.textContent.trim();
                }

                if (pageId === "export-center") {
                    loadExportHistory();
                }
            },
            true
        );
    }

    function initializeButtons() {
        $("#export-json")?.addEventListener("click", () => {
            generateExport("JSON");
        });

        $("#export-html")?.addEventListener("click", () => {
            generateExport("HTML");
        });

        $("#refresh-exports")?.addEventListener("click", () => {
            loadExportHistory();
        });
    }

    function initialize() {
        if (!createDashboard()) {
            return;
        }

        initializeNavigation();
        initializeButtons();

        loadExportHistory();

        console.log("[NEMESIS] Export Center initialized.");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();
