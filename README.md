

\# NEMESIS



\*\*Adversary Research \& Emulation System\*\*



NEMESIS is a Windows-based local defensive security assessment, inert event simulation, detection analytics, and reporting platform.



\## Version



1.0.0



\## Project Scope



NEMESIS is designed for authorized local security research and defensive validation.



The application runs locally at:



`http://127.0.0.1:8765`



It does not provide remote network scanning, unauthorized access, credential attacks, or real attack execution.



\## Technology Stack



\- Python

\- Flask

\- SQLite

\- HTML, CSS, JavaScript

\- Windows



\## Core Modules



1\. \*\*Reconnaissance\*\* — local system inventory.

2\. \*\*Security Assessment\*\* — read-only Windows security checks.

3\. \*\*Simulation Lab\*\* — inert local security event generation.

4\. \*\*Detection Engine\*\* — matching simulated events to detection rules.

5\. \*\*Threat Intelligence\*\* — candidate MITRE ATT\&CK references.

6\. \*\*Detection Analytics\*\* — analysis of stored simulation records.

7\. \*\*Security Monitoring\*\* — read-only simulation timeline.

8\. \*\*Unified Reporting\*\* — combined assessment and simulation reports.

9\. \*\*Executive Dashboard\*\* — summary of local project metrics.

10\. \*\*Export Center\*\* — JSON and standalone HTML report exports.



\## Installation



Open Command Prompt in the project directory.



Create and activate a virtual environment:



```cmd

python -m venv venv

venv\\Scripts\\activate

```



Install dependencies:



```cmd

python -m pip install -r requirements.txt

```



\## Run NEMESIS



```cmd

python app.py

```



Open the local dashboard:



`http://127.0.0.1:8765`



The server is configured for local access.



\## Run Tests



```cmd

python -m unittest discover -v

```



\## Project Structure



```text

NEMESIS/

├── app.py

├── config.py

├── database/

├── docs/

├── integration/

├── logs/

├── modules/

│   ├── assessment/

│   ├── detection\_analytics/

│   ├── monitoring/

│   ├── simulation/

│   ├── threat\_intelligence/

│   └── unified\_reporting/

├── reports/

├── scripts/

├── static/

│   ├── css/

│   └── js/

├── templates/

├── tests/

├── requirements.txt

└── README.md

```



\## Reporting



NEMESIS supports:



\- Local assessment JSON and HTML reports.

\- Unified security report API.

\- Unified JSON export.

\- Unified standalone HTML export.

\- Export history and downloads.



Exported reports may contain local security assessment information. Keep them private.



\## Data Scope and Limitations



\- Reconnaissance collects local inventory information.

\- Assessment checks are read-only.

\- Simulation events are inert and do not execute real attacks.

\- Detection coverage applies only to stored simulation records.

\- MITRE ATT\&CK references are candidate mappings, not confirmed attack evidence.

\- Monitoring displays stored simulation events, not live endpoint telemetry.

\- SENTINEL X integration currently checks directory existence only.



\## Documentation



\- `docs/USER\_GUIDE.md`

\- `docs/API\_REFERENCE.md`

\- `docs/BACKUP\_RECOVERY.md`



\## Authorization



Use NEMESIS only on systems you own or are explicitly authorized to assess.



Do not use this application to access, disrupt, or test third-party systems without permission.



