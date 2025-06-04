# 🏒 NHL Season Analytics Web App

This project is a Flask-based web application that displays NHL season statistics. Data is gathered from NHL.com through kaggle and other resources, then stored in a relational database ( SQLite). A simple web interface allows users to explore game and team data interactively.

> ⚠️ Originally designed to include machine learning models for predictive analytics, this version focuses solely on data ingestion, storage, and visualization.

---

## 🔑 Key Features

- **📊 Data Collection:** Pulls NHL statistics using public API calls and web scraping.
- **🗃️ Relational Database:** Stores structured data (games, teams, players) in SQLite.
- **🌐 Flask Web UI:** Interactive interface for querying and viewing the data.

---

## 🚧 Project Status

- ✅ Database schema and sample data implemented and tested.
- ✅ Flask frontend is live and integrated with the database.
- ❌ Machine learning features not included in this version.

---

## ⚙️ Setup & Installation

### 🔗 Prerequisites

- Python 3.x
- `pip` package manager
- SQLite (default)
Install the required packages:

```bash
pip install flask requests beautifulsoup4
```

1. **Clone the Repository**
Clone the repository and then follow the instructions below:
   
bash
   ```bash
cd nhl-season-analytics
```

**Set Up the Database**

To initialize the database, run the following Bash command from the project's base folder:

```bash
flask --app flaskr init-db
```

This will set up the database schema and load initial data. SQLite is used by default for testing, but you can modify the application to use PostgreSQL for production.

**Run the Flask Application**

To start the Flask web server run:

```bash
flask --app flaskr run --debug
```

This will start the development server, and the application should be accessible in your browser at http://127.0.0.1:5000/.

Note: This is a work in progress
