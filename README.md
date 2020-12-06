# PropelPrompt

1. Overview
1. Setup
1. Flask App
1. HTML Pages

## Overview

PropelPrompt is a web application that allows users to set goals, plan tasks, and better manage their time through analytics, so that they develop productive working habits and stay motivated. PropelPrompt is designed to function as a companion app while a user focuses on their work. The app helps the user track how much time they spend on various tasks and prompts the user to reflect on their work sessions. The aim is that users are more cognisant of their time management skills, and deliberate about how they plan and achieve their goals.

The index, register and login page feature open source illustrations from <a href=“unDraw.co”>unDraw</a>.

## Setup

To run the app locally, download all the files above. Make sure that the file structure is preserved.

(1) Navigate to the application through your terminal. (2) Run ```console pip3 install -r requirements.txt``` to install all necessary python requirements. (3) Open and run setup_sql.py to create the sql database. This should create a new file called site.db. (4) Launch the flask application from your terminal by running ```console python3 app.py```  (5) If any packages are still missing at this point, run ```pip3 install <package_name>``` and repeat (4) until the app launches. (5) Open your browser (chrome recommended) and type 0.0.0.0. You can now register a new account and get started.
