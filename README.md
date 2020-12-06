# PropelPrompt

1. Overview
1. Setup
1. User Guide
1. Technical Implementation
1. Challenges and Solutions 

## Overview

PropelPrompt is a web application that allows users to set goals, plan tasks, and better manage their time through analytics, so that they develop productive working habits and stay motivated. PropelPrompt is designed to function as a companion app while a user focuses on their work. The app helps the user track how much time they spend on various tasks and prompts the user to reflect on their work sessions. The aim is that users are more cognisant of their time management skills, and deliberate about how they plan and achieve their goals.

The index, register and login page feature open source illustrations from <a href=“unDraw.co”>unDraw</a>.

## Setup

To run the app locally, download all the files above. Make sure that the file structure is preserved.

(1) Navigate to the application through your terminal.

(2) Run ```console pip3 install -r requirements.txt``` to install all necessary python requirements.

(3) Open and run setup_sql.py to create the sql database. This should create a new file called site.db.

(4) Launch the Flask application from your terminal by running ```console python3 app.py```.

(5) If any packages are still missing at this point, run ```pip3 install <package_name>``` and repeat (4) until the app launches.

(6) Launch your browser (chrome recommended) and type 0.0.0.0. You can now register a new account and get started.

## User Guide

From the landing page, you can navigate to register a new account or log in. Once you have logged in, you are redirected to your workspace. From your workspace, you can start a new session, schedule reminders, and navigate to your goals or profile. To get started as a new user, navigate to your goals and set a new goal by specifying the goal and adding a short description. Each goal links to a separate page where you can set tasks. Set a new task and navigate back to your workspace. You can schedule reminders to work on certain goals on right hand side of the screen, or start a session. A session helps you track how much time you spend working on your tasks. After starting a session, select a goal and a task. When you are done working, end your session. After you end a session, specify whether you have completed your task, and, if you wish, attach a note for yourself. Completing a task will delete it from your task tab. Your profile tab displays a summary of your working habits and logs all your sessions by day.

## Technical Implementation

The application uses the Flask web framework, the Jinja template engine to pass variables from python to HTML, the flask_sqlalchemy package to setup a database, and Bootstrap to create a responsive web interface. Bcrypt is used to encrypt user passwords.

First, required packages are imported, then Flask form classes and login/registration functions are defined before the app is instantiated. Afterwards, several classes are defined for each database table. Finally, each web route is defined. Most routes include a flask form which allows users to post information, which is then displayed and stored for later use. Each return statement either renders an HTML page, located in the templates folder, or redirects the user to an HTML page. Each route that the user is retried to login for, includes an @login_required statement. This is important because data is often queried by the current user id e.g, ‘’’ Goal.query.filter_by(user_id = current_user.user_id)’’’, which requires a user to be logged in.

## Challenges and Solutions

