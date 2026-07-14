# AI-Based Rising Water Detection and Flood Early Warning System

## Project Overview
This project provides an AI-powered flood early warning system that monitors water and weather indicators, predicts flood severity using machine learning, and displays a modern dashboard for analysis and alerts.

## Objectives
- Detect rising water risks using machine learning.
- Provide a responsive dashboard for monitoring and alerts.
- Support user authentication and admin operations.
- Store and analyze historical prediction data.

## Features
- Authentication and session management
- Dashboard with real-time metrics
- Prediction engine with trained ML model
- Analytics and reporting
- Admin panel for managing users and logs

## Technologies Used
- Frontend: HTML, CSS, Bootstrap, JavaScript, Chart.js
- Backend: Flask, Python
- ML: Pandas, NumPy, Scikit-learn, Joblib
- Database: SQLite

## Installation
1. `cd 05_Project Development Phase/project`
2. `pip install -r requirements.txt`
3. `python train_model.py`
4. `python app.py`

## Folder Structure
- `dataset/` contains synthetic flood data.
- `models/` stores the trained model.
- `templates/` contains the UI pages.
- `static/` contains styles and scripts.

## Dataset Description
The dataset contains water level, rainfall, temperature, humidity, river flow, soil moisture, water velocity, flood history, and prediction labels.

## Machine Learning Workflow
1. Generate dataset
2. Clean and preprocess data
3. Train multiple classifiers
4. Compare accuracy
5. Save the best model as `models/model.pkl`

## Screenshots
The demonstration folder contains sample dashboard and prediction screenshots.

## Future Scope
- Real sensor integration
- SMS and email alerts
- GIS mapping and geospatial analysis

## Team Members
- Team Lead: SmartBridge Project Team
- Developer: Full Stack + AI/ML Engineer

## License
This project is developed for educational and demonstration purposes.
