

\# NEMESIS Backup and Recovery Guide



\## 1. Purpose



This guide describes how to create and restore a local NEMESIS project backup.



\## 2. Backup Contents



The backup script includes available project files and directories, including:



\- Application source code.

\- Configuration.

\- Modules.

\- Templates and static assets.

\- Tests and documentation.

\- SQLite databases.

\- Generated reports.

\- Requirements file.



The script excludes:



\- Virtual environments.

\- Python cache directories.

\- Log directories.

\- Existing backup archives.

\- Git metadata.

\- Temporary and compiled Python files.



\## 3. Before Creating a Backup



1\. Stop the Flask server using `CTRL + C`.

2\. Confirm the NEMESIS project directory is accessible.

3\. Ensure sufficient disk space is available.

4\. Keep the backup on a private local drive.



Stopping Flask first helps avoid copying a database while it is being modified.



\## 4. Create a Backup



Activate the virtual environment, then run:



`python scripts\\backup.py`



The archive is created inside:



`backups`



The filename contains a timestamp.



\## 5. Verify a Backup



The backup script prints the archive filename, file count, and archive size.



Check that the ZIP archive exists in the `backups` directory.



Do not share the archive publicly.



\## 6. Restore a Backup



1\. Create a separate empty recovery directory.

2\. Extract the selected ZIP archive into that directory.

3\. Inspect the restored files.

4\. Create a new virtual environment.

5\. Install dependencies:



&#x20;  `python -m pip install -r requirements.txt`



6\. Run the tests:



&#x20;  `python -m unittest discover -v`



7\. Start the application:



&#x20;  `python app.py`



8\. Verify the dashboard and local data.



Do not extract an old backup directly over an active project. Restore into a separate directory first.



\## 7. Data Protection



Database files and generated reports may contain local system information.



Store backups securely and restrict access to trusted users.



Do not upload backups to public file-sharing services.



