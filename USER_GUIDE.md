

\# NEMESIS User Guide



\## 1. Starting the Application



1\. Open Command Prompt.

2\. Navigate to the NEMESIS project directory.

3\. Activate the virtual environment:



&#x20;  `venv\\Scripts\\activate`



4\. Start the application:



&#x20;  `python app.py`



5\. Open `http://127.0.0.1:8765` in a browser.



\## 2. Dashboard Overview



The Overview page displays application status, local assessment counts, and module navigation.



\## 3. Reconnaissance



The Reconnaissance module collects local system inventory information.



Use \*\*RUN RECON\*\* to start the local inventory operation.



Reconnaissance results may contain sensitive machine and network information. Do not publish raw results.



\## 4. Security Assessment



The Assessment module performs read-only local security checks, including supported Windows Firewall and Defender status checks.



Use \*\*RUN ASSESSMENT\*\* to execute the checks.



Results are stored locally in SQLite.



\## 5. Simulation Lab



The Simulation Lab generates inert local events for defensive detection validation.



Available scenarios:



\- AUTH-001 — Failed Login Event

\- FW-001 — Firewall Configuration Alert

\- EDR-001 — Unusual Process Alert

\- ACCESS-001 — Privilege Change Event



These scenarios create simulated records only. They do not perform real authentication attempts, modify system settings, or execute attack commands.



\## 6. Threat Intelligence



Displays the local scenario catalog and candidate MITRE ATT\&CK references.



Candidate mappings must not be interpreted as confirmed evidence of an attack.



\## 7. Detection Analytics



Displays statistics derived from stored simulation records.



Detection coverage represents the proportion of analyzed stored simulation records marked as detected. It is not a measurement of real-world security effectiveness.



\## 8. Security Monitoring



Displays a read-only timeline and summary of stored inert simulation events.



This module is not live endpoint monitoring.



\## 9. Integration



The current SENTINEL X integration checks whether the configured local directory exists.



Directory detection does not mean that a complete integration has been configured.



\## 10. Report Center



The Report Center provides assessment reports.



Users can open HTML reports and download JSON reports.



\## 11. Export Center



The Export Center provides:



\- Generate JSON — creates and downloads a unified JSON report.

\- Generate HTML — creates and downloads a standalone HTML report.

\- Refresh History — reloads the export list.

\- Download — downloads an existing export.



Exported files are stored in the local `reports` directory.



Keep exported files private because they may contain local assessment information.



\## 12. Troubleshooting



\### Application does not start



Check that the virtual environment is active and dependencies are installed.



Run:



`python -m pip install -r requirements.txt`



\### Dashboard does not show recent changes



Restart Flask and perform a hard browser refresh with `CTRL + F5`.



\### API returns 404



Confirm the server was restarted after route changes. Check that the requested endpoint is registered in `app.py`.



\### Tests fail



Run the relevant test module separately, then run the complete test suite:



`python -m unittest discover -v`



\## 13. Safe Operation



Use the application only in an authorized local environment.



Do not publish raw reconnaissance output, database files, or generated reports.



