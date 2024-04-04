# CMS Identifier Tool

==CMS Identifier Tool== is a Python application designed to detect the Content Management System (CMS) used by a given website. The tool provides both a command-line interface and a graphical user interface (GUI) for ease of use.



## *Features*

* Support for single URL checking or bulk URL processing from a file.

* User-Agent spoofing to mimic browser requests.

* Asynchronous HTTP requests for efficient and fast scanning.

* SQLite database integration for CMS pattern matching.

* Simple and intuitive GUI for users who prefer a graphical interface.



## *Command-Line Usage*

To use the CMS Identifier from the command line, navigate to the directory containing the script and run the following commands as per your requirement:

```
# Check a single URL:
python cms_identifier.py -u "http://example.com"


# Check URLs from a file:
python cms_identifier.py -r "urls.txt"


# Enable User-Agent spoofing:
python cms_identifier.py -u "http://example.com" -ua
```



Make sure the SQLite database is in the same directory as the script or update the script to point to the correct location.cms_finger.db



## GUI Application

To launch the GUI application, run the Python script that initializes the class.==CMSIdentifierApp==

```
python cms_identifier_gui.py
```

Once the GUI is open, you can:

* **Add a URL manually using the "Add URL" button.**

* **Load a list of URLs from a file using the "Select URL File" button.**

* **Start the CMS detection process using the "Start" button.**

* **View the results in the scrolled text area within the app.**



## Requirements

* ***Python 3.x***

* ***==aiohttp== library for asynchronous HTTP requests.***

* ***==tkinter== library for GUI creation.***

* ***==sqlite3== library for SQLite database access.***

* ***A SQLite database with CMS patterns.==cms_finger.db==***



## Installation

Before running the tool, ensure you have the required libraries:

```
pip install -r requirements.txt
```

==tkinter== usually comes pre-installed with Python. If for somea reason it's not available, it can be installed using your distribution's package manager.



## Database Setup

Create a SQLite database named and populate it with the necessary tables and data for CMS patterns. The expected table structure is:cms_finger.db

```sql
CREATE TABLE cms (
    path TEXT,
    match_pattern TEXT,
    cms_name TEXT,
    options TEXT
);
```

Fill this table with CMS paths, match patterns, CMS names, and options (e.g., 'keyword' or 'md5') for comparison.



# Conclusion

The is a versatile tool that helps users and web administrators to quickly identify the CMS used by a website, which can be crucial for research, security testing, and more.==CMS Identifier Tool==

## **Please use this tool responsibly and only on websites you have permission to scan.**

