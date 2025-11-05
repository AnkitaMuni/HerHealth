<div align="center">
<strong>HerHealth</strong>
</div>

<div align="center">
<strong>Menstrual Cycle Tracker & Health Dashboard</strong>
</div>

<br />

A comprehensive, data-driven web application built with Python and Flask, designed to help users track their menstrual cycles, log health data, and gain insights through personalized predictions and data visualizations.

<br />

📖 Table of Contents:
<br/>
  ✨ Key Features
  <br/>
  🚀 Advanced Database Features
  <br/>
  💻 Tech Stack
  <br/>
  🚀 How to Run This Project
  
<br/>

✨ Key Features:

Secure User Authentication: Full registration and login system with password hashing using bcrypt.<br/>
Personalized Dashboard: The main hub for users, showing:<br/>
AI-Powered Predictions: Displays the predicted start date and duration of the next cycle.<br/>
Dynamic Notifications: Generates live alerts, such as "Your next cycle is predicted to start in X days."<br/>
Actionable Notifications: Shows database-driven reminders (e.g., "Check supplies") that can be dismissed by the user.<br/>
Data Visualization: Renders charts for Weight & Height Log and Cycle Analytics (Period Duration vs. Full Cycle Length) using Chart.js.<br/>
Cycle & Medicine Logging: Easy-to-use forms for users to log:<br/>
Cycles: Start date, end date, mood, weight, and height.<br/>
Medicines: Name of medicine, dosage, and an option to upload a doctor's consultation file (stored in the database as a BLOB).<br/>
Complete History: A chronological view of all past cycles and associated medications.<br/>
User Profile: A dedicated page to view all registered user details.<br/>

🚀 Advanced Database Features (MySQL)

This project heavily utilizes advanced database features to manage data and automate tasks:<br/>
Triggers: A before_insert_prediction_dates trigger automatically populates NULL dates in a new prediction record by copying them from its linked notification record.<br/>
Stored Functions: get_latest_medication_dosage() allows the application to query for the most recent dosage a user logged for a specific medicine.<br/>
Stored Procedures: archive_completed_notifications() is a maintenance procedure that moves all "completed" notifications older than X days from the main table to an notification_archive table, keeping the primary table clean.<br/>
Complex Queries: The database schema is supported by several complex analytical queries (using JOIN, LAG(), RANK(), GROUP BY, etc.) to find lapsed users, calculate average BMI, and more.<br/>

💻 Tech Stack

Backend: Python, Flask<br/>
Database: MySQL<br/>
Python Libraries: mysql-connector-python (for DB connection), bcrypt (for password hashing)<br/>
Frontend: HTML, CSS, JavaScript, Chart.js (for data visualization)<br/>
Templating: Jinja2 (via Flask)<br/>

🚀 How to Run This Project

Follow these steps to set up and run the project locally.

1. Prerequisites

Python 3.7+

A running MySQL Server instance

2. Clone the Repository

git clone https://github.com/AnkitaMuni/HerHealth.git <br/>
cd HerHealth


3. Set Up a Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate


4. Install Python Dependencies

Install all the required libraries from the requirements.txt file.

pip install -r requirements.txt


5. Set Up the MySQL Database

You must run your herhealth.sql file (or equivalent setup script) on your MySQL server. This script should do the following:

Create the herhealth database.

Create all tables: user, cycle, medicine, notification, prediction, and notification_archive.

Create the trigger: before_insert_prediction_dates.

Create the function: get_latest_medication_dosage.

Create the procedure: archive_completed_notifications.

You can do this using the MySQL command line:

-- Log in to MySQL
mysql -u root -p

-- Create the database and exit
mysql> CREATE DATABASE herhealth;
mysql> exit;

-- Run the SQL script to create all tables, triggers, etc.
mysql -u root -p herhealth < herhealth.sql


6. Configure the Database Connection

Open the db_connector.py file (or wherever your connection is defined) and update the get_db_connection() function with your MySQL username and password.

# Inside db_connector.py
<br/>
def get_db_connection():<br/>
    try:<br/>
        conn = mysql.connector.connect(<br/>
            host="localhost",       # Or your DB host<br/>
            user="YOUR_USERNAME",   # <-- UPDATE THIS<br/>
            password="YOUR_PASSWORD", # <-- UPDATE THIS<br/>
            database="herhealth"<br/>
        )<br/>
        return conn<br/>
    # ...<br/>
<br/>

7. Run the Flask Application

Once the database is set up and the dependencies are installed, run the main app.py file.

python app.py


8. Access the Application

Your project is now running! Open your web browser and go to:

http://127.0.0.1:5000
