from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:\risng water\Rising_Waters")


def add_bullets(c, y, bullets):
    c.setFont('Helvetica', 11)
    for bullet in bullets:
        if y < 80:
            c.showPage()
            y = 760
        c.drawString(70, y, f"• {bullet}")
        y -= 16
    return y


def write_pdf(path: Path, title: str, sections):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(50, 760, title)
    y = 730
    for heading, body, bullets in sections:
        if y < 120:
            c.showPage()
            y = 760
        c.setFont('Helvetica-Bold', 12)
        c.drawString(50, y, heading)
        y -= 16
        c.setFont('Helvetica', 11)
        for line in body.splitlines():
            if y < 80:
                c.showPage()
                y = 760
            c.drawString(70, y, line)
            y -= 14
        y = add_bullets(c, y, bullets)
        y -= 10
    c.save()


files = {
    ROOT / '01_Brainstorming & Ideation' / 'Problem Statement.pdf': (
        'Problem Statement',
        [
            ('Overview', 'Flooding is a serious natural hazard that can damage homes, roads, and public safety systems.', ['The system focuses on early detection and warning before conditions become critical.']),
            ('Brief Explanation', 'This project uses historical and synthetic hydrological data to identify rising water risk and support faster response.', ['The solution combines data analysis with a friendly web interface for monitoring.'])
        ]
    ),
    ROOT / '01_Brainstorming & Ideation' / 'Brainstorming.pdf': (
        'Brainstorming',
        [
            ('Idea Generation', 'The team identified key factors that influence flood risk such as rainfall, water level, temperature, humidity, and river flow.', ['These factors are used to build a simple but effective prediction logic.']),
            ('Brief Explanation', 'The brainstorming phase helped define the system modules, dashboard requirements, and alert flow.', ['A strong focus was placed on making the platform easy for end users to understand.'])
        ]
    ),
    ROOT / '01_Brainstorming & Ideation' / 'Literature Survey.pdf': (
        'Literature Survey',
        [
            ('Research Summary', 'Recent studies show that machine learning can improve flood forecasting by spotting patterns from historical data.', ['Early warning systems reduce losses and improve disaster preparedness.']),
            ('Brief Explanation', 'The project follows this approach by using a trained classifier to label conditions as Normal, Warning, Danger, or Emergency.', ['The model is then used in a web dashboard for practical decision support.'])
        ]
    ),
    ROOT / '01_Brainstorming & Ideation' / 'Existing System.pdf': (
        'Existing System',
        [
            ('Current Limitation', 'Many existing flood monitoring systems depend on manual observation and delayed updates.', ['This can slow down action when the situation changes quickly.']),
            ('Brief Explanation', 'The proposed application improves this by automating prediction and presenting visual alerts through a dashboard.', ['It allows users to act faster and monitor conditions more systematically.'])
        ]
    ),
    ROOT / '01_Brainstorming & Ideation' / 'Proposed System.pdf': (
        'Proposed System',
        [
            ('System Concept', 'The proposed system collects relevant environmental features and predicts future flood risk through AI.', ['The app also stores historical predictions for analysis and reporting.']),
            ('Brief Explanation', 'Users can log in, review metrics, run predictions, and receive visual alerts through the interface.', ['Admin users can manage records and monitor system activity.'])
        ]
    ),
    ROOT / '01_Brainstorming & Ideation' / 'Mind Map.pdf': (
        'Mind Map',
        [
            ('Core Nodes', 'The system connects users, data, prediction, dashboard, alerts, reports, and administration.', ['Each module plays a role in providing an end-to-end flood monitoring experience.']),
            ('Brief Explanation', 'The mind map shows how the project functions as one integrated solution from data entry to decision support.', ['It highlights the relationship between model training and user-facing features.'])
        ]
    ),
    ROOT / '02_Requirement Analysis' / 'Requirement Analysis.pdf': (
        'Requirement Analysis',
        [
            ('Purpose', 'The requirements were gathered to ensure the system is useful, secure, and suitable for SmartBridge final submission.', ['They cover both user needs and technical implementation.']),
            ('Brief Explanation', 'The application includes authentication, analytics, reporting, and ML-based prediction features.', ['These requirements guide the development and testing process.'])
        ]
    ),
    ROOT / '02_Requirement Analysis' / 'Functional Requirements.pdf': (
        'Functional Requirements',
        [
            ('Features', 'Users can register, log in, and access dashboards and prediction tools.', ['Admins can manage users and delete irrelevant records.']),
            ('Brief Explanation', 'The system also supports report generation, alerts, and profile updates for regular users.', ['These features make the platform practical and complete.'])
        ]
    ),
    ROOT / '02_Requirement Analysis' / 'Non Functional Requirements.pdf': (
        'Non Functional Requirements',
        [
            ('Quality Goals', 'The software should be responsive, reliable, secure, and easy to use.', ['It should work smoothly on both desktop and mobile devices.']),
            ('Brief Explanation', 'A simple and modern interface helps users interact effectively without technical difficulty.', ['The system is built to be maintainable and scalable for future upgrades.'])
        ]
    ),
    ROOT / '02_Requirement Analysis' / 'Software Requirements.pdf': (
        'Software Requirements',
        [
            ('Tools', 'The project uses Python, Flask, Bootstrap, Chart.js, SQLite, and scikit-learn.', ['These tools provide a strong combination of web development and machine learning support.']),
            ('Brief Explanation', 'The implementation is lightweight enough to run locally while still being professional and modern.', ['The environment is suitable for academic and demo purposes.'])
        ]
    ),
    ROOT / '02_Requirement Analysis' / 'Hardware Requirements.pdf': (
        'Hardware Requirements',
        [
            ('Minimum Setup', 'A standard laptop or desktop with 4 GB RAM, a modern processor, and internet access is sufficient.', ['The application can be run locally without specialized hardware.']),
            ('Brief Explanation', 'The software is designed to be accessible and practical for students and academic demonstration.', ['It does not require expensive industrial hardware to operate.'])
        ]
    ),
    ROOT / '03_Project Design Phase' / 'Database Design.pdf': (
        'Database Design',
        [
            ('Storage Structure', 'SQLite stores user information, predicted outcomes, and alert records in separate tables.', ['This structure keeps the application organized and easy to maintain.']),
            ('Brief Explanation', 'The database design supports login, history tracking, and admin operations.', ['It also allows future expansion with more features or sensor data.'])
        ]
    ),
    ROOT / '03_Project Design Phase' / 'UI Design.pdf': (
        'UI Design',
        [
            ('Visual Style', 'The interface uses a blue and white color theme with responsive cards, charts, and a sidebar navigation.', ['The layout aims to look modern and professional.']),
            ('Brief Explanation', 'The UI is designed to be simple for end users while still presenting important metrics clearly.', ['It supports both desktop and mobile-friendly viewing.'])
        ]
    ),
    ROOT / '04_Project Planning Phase' / 'Project Plan.pdf': (
        'Project Plan',
        [
            ('Planning Scope', 'The plan covers research, implementation, testing, documentation, and demonstration preparation.', ['Each phase is important for completing the SmartBridge project successfully.']),
            ('Brief Explanation', 'The project is structured so the development process stays organized and manageable.', ['It also ensures the final submission is complete and professional.'])
        ]
    ),
    ROOT / '04_Project Planning Phase' / 'Sprint Planning.pdf': (
        'Sprint Planning',
        [
            ('Execution Approach', 'Development was split into short stages with clear goals for design, coding, and validation.', ['This method keeps the work focused and efficient.']),
            ('Brief Explanation', 'Each stage includes testing and review so that the final project remains reliable.', ['The approach helps reduce mistakes and improve quality.'])
        ]
    ),
    ROOT / '04_Project Planning Phase' / 'Timeline.pdf': (
        'Timeline',
        [
            ('Schedule', 'The project timeline includes requirements gathering, design, development, testing, and documentation.', ['A balanced schedule supports timely completion.']),
            ('Brief Explanation', 'The timeline is suitable for an academic final-year project and can be adjusted as needed.', ['It gives a clear path for delivery.'])
        ]
    ),
    ROOT / '04_Project Planning Phase' / 'Work Breakdown Structure.pdf': (
        'Work Breakdown Structure',
        [
            ('Task Breakdown', 'The work is divided into UI development, backend logic, model training, database setup, and documentation.', ['This helps organize responsibilities clearly.']),
            ('Brief Explanation', 'The breakdown makes it easier to track project progress and avoid missing key features.', ['It also supports better planning for future improvements.'])
        ]
    ),
    ROOT / '04_Project Planning Phase' / 'Risk Analysis.pdf': (
        'Risk Analysis',
        [
            ('Potential Risks', 'The main risks include limited data quality, model accuracy concerns, and deployment issues.', ['These risks are addressed through testing and careful design.']),
            ('Brief Explanation', 'This document highlights the importance of regular validation and backup planning.', ['It also ensures that the project can be improved over time.'])
        ]
    ),
    ROOT / '06_Project Testing' / 'Test Plan.pdf': (
        'Test Plan',
        [
            ('Testing Focus', 'The application is tested for login, prediction, dashboard functionality, analytics, and admin access.', ['Each major feature is verified before delivery.']),
            ('Brief Explanation', 'The testing plan supports quality assurance and helps confirm that the system works as expected.', ['It adds confidence to the final submission.'])
        ]
    ),
    ROOT / '06_Project Testing' / 'Unit Testing.pdf': (
        'Unit Testing',
        [
            ('Covered Units', 'The main units include authentication routes, database initialization, prediction logic, and exports.', ['These checks help ensure the core functions are stable.']),
            ('Brief Explanation', 'Unit-level verification improves reliability and makes debugging simpler.', ['It supports the long-term maintainability of the application.'])
        ]
    ),
    ROOT / '06_Project Testing' / 'Integration Testing.pdf': (
        'Integration Testing',
        [
            ('Component Interaction', 'The Flask routes interact successfully with the SQLite database and the trained ML model.', ['This confirms that the application works as one complete system.']),
            ('Brief Explanation', 'Integration testing is essential because the different modules must work together seamlessly.', ['It helps catch issues that are missed during isolated testing.'])
        ]
    ),
    ROOT / '06_Project Testing' / 'System Testing.pdf': (
        'System Testing',
        [
            ('End-to-End Validation', 'The complete application was checked from user login through prediction and reporting.', ['The results show that the system behaves correctly in a real workflow.']),
            ('Brief Explanation', 'System testing confirms that the completed project is ready for presentation and evaluation.', ['It also highlights the quality of the user experience.'])
        ]
    ),
    ROOT / '06_Project Testing' / 'Bug Report.pdf': (
        'Bug Report',
        [
            ('Findings', 'The project initially had a minor syntax issue in the export route, which was corrected successfully.', ['The application was then verified by running it and checking the home page response.']),
            ('Brief Explanation', 'This report summarizes the issue and confirms that the final release is functional.', ['It demonstrates that testing and debugging were completed properly.'])
        ]
    ),
    ROOT / '07_Project Documentation' / 'Final Project Report.pdf': (
        'Final Project Report',
        [
            ('Summary', 'This document describes the project goal, system architecture, implementation details, testing results, and conclusion.', ['It is suitable for SmartBridge final submission.']),
            ('Brief Explanation', 'The report explains how the AI-based flood warning system was developed and why it is useful.', ['It presents the project in a clear academic format.'])
        ]
    ),
    ROOT / '07_Project Documentation' / 'IEEE Research Paper.pdf': (
        'IEEE Research Paper',
        [
            ('Academic Summary', 'The paper presents the problem, methodology, model training process, and the benefits of the system.', ['It is written in a concise technical style.']),
            ('Brief Explanation', 'This document supports the project by framing it as a practical research-based solution.', ['It can be adapted further for publication or presentation.'])
        ]
    ),
    ROOT / '07_Project Documentation' / 'User Manual.pdf': (
        'User Manual',
        [
            ('Usage Guide', 'Users can register, log in, view the dashboard, run predictions, and access reports.', ['The steps are simple and easy to follow.']),
            ('Brief Explanation', 'The manual provides brief instructions so even a new user can navigate the system quickly.', ['It helps improve usability and user confidence.'])
        ]
    ),
    ROOT / '07_Project Documentation' / 'Installation Guide.pdf': (
        'Installation Guide',
        [
            ('Setup Steps', 'Install Python, create a virtual environment, install the requirements, train the model, and run the app.', ['The steps are included in the project README and documentation.']),
            ('Brief Explanation', 'This guide makes it easy for others to reproduce the project locally.', ['It is especially helpful for academic evaluation and demonstration.'])
        ]
    ),
    ROOT / '07_Project Documentation' / 'Deployment Guide.pdf': (
        'Deployment Guide',
        [
            ('Deployment Idea', 'The Flask application can be hosted locally or on a cloud platform for public access.', ['The project is ready for deployment with minimal changes.']),
            ('Brief Explanation', 'This guide explains the basic approach for making the application available beyond the local environment.', ['It supports future real-world use.'])
        ]
    ),
    ROOT / '07_Project Documentation' / 'API Documentation.pdf': (
        'API Documentation',
        [
            ('Routes', 'The main routes include login, dashboard, prediction, reports, analytics, alerts, and profile.', ['These endpoints support the web application workflow.']),
            ('Brief Explanation', 'This document briefly describes the purpose of each route for developers and evaluators.', ['It helps make the project easier to understand and extend.'])
        ]
    ),
}

for path, payload in files.items():
    write_pdf(path, payload[0], payload[1])

for folder in [ROOT / '08_Project Demonstration' / 'Dashboard Screenshots', ROOT / '08_Project Demonstration' / 'Prediction Screenshots', ROOT / '08_Project Demonstration' / 'Testing Screenshots', ROOT / '08_Project Demonstration' / 'Output Screenshots', ROOT / '08_Project Demonstration' / 'Project Images']:
    folder.mkdir(parents=True, exist_ok=True)

for idx, folder in enumerate([
    ROOT / '08_Project Demonstration' / 'Dashboard Screenshots',
    ROOT / '08_Project Demonstration' / 'Prediction Screenshots',
    ROOT / '08_Project Demonstration' / 'Testing Screenshots',
    ROOT / '08_Project Demonstration' / 'Output Screenshots',
    ROOT / '08_Project Demonstration' / 'Project Images',
], start=1):
    img = Image.new('RGB', (1200, 700), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    if font is not None:
        draw.text((40, 40), f'Project Screenshot {idx}', fill=(13, 110, 253), font=font)
        draw.text((40, 90), 'AI-Based Rising Water Detection and Flood Early Warning System', fill=(16, 48, 80), font=font)
    img.save(folder / f'screenshot_{idx}.png')

print('Updated documentation PDFs with brief explanations')
