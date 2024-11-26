# NHL Season Analytics & Prediction Model

This project is designed to collect, analyze, and visualize data from the current NHL season using web scraping and API calls to NHL.com. The data is stored in a relational database, likely PostgreSQL, and is leveraged in complex machine learning models to provide predictive insights and analytics. The ultimate goal is to build a model that can predict future game outcomes and potentially outperform betting odds set by Vegas.

The project also includes a user interface (UI) built with Flask, allowing users to interact with the data and view the results of machine learning predictions.

## Key Features

- **Data Collection:** Web scraping and API calls to gather up-to-date NHL season statistics from NHL.com.
- **Relational Database:** Data is stored in a PostgreSQL (or SQLite for testing) relational database for easy querying and management.
- **Machine Learning Models:** The application utilizes machine learning algorithms to analyze historical data and generate predictions for upcoming games, with a focus on overtime.
- **Flask Web UI:** A basic web interface built with Flask to interact with the data, view insights, and access prediction results.

## Current Status

- **Database Design:** A relational database schema has been designed to store the NHL season data. A test implementation has been created using SQLite with a small set of accurate data for initial testing.
- **Web UI:** The basic pages of the user interface are functional and connected to the database. The Flask app allows users to query and visualize the data.

## Setup & Installation

### Prerequisites
- Python 3.x
- SQLite (for testing) or PostgreSQL
- Flask

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/nhl-season-analytics.git
   cd nhl-season-analytics

**Set Up the Database**

To initialize the database, run the following Bash command from the project's base folder:

flask --app flaskr init-db

This will set up the database schema and load initial data. SQLite is used by default for testing, but you can modify the application to use PostgreSQL for production.

**Run the Flask Application**

To start the Flask web server run:

flask --app flaskr run --debug

This will start the development server, and the application should be accessible in your browser at http://127.0.0.1:5000/.

Note: This is a work in progress, continuously adding new features and improving existing ones. Stay tuned for updates!

