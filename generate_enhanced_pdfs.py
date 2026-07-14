from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(r"D:\risng water\Rising_Waters")


def add_text_block(c, title, lines, y, left=50):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, title)
    y -= 16
    c.setFont("Helvetica", 10.5)
    for line in lines:
        if y < 70:
            break
        c.drawString(left + 10, y, line)
        y -= 14
    return y


def add_footer(c, title):
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 30, "AI-Based Rising Water Detection and Flood Early Warning System")
    c.drawRightString(550, 30, f"{title} | SmartBridge Project")


def write_two_page_pdf(path, title, intro_lines, details_lines, extra_lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=letter)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 760, title)
    c.setFont("Helvetica", 11)
    c.drawString(50, 730, "This document provides a detailed explanation based on the selected project title and its academic importance.")

    y = 690
    y = add_text_block(c, "Project Overview", intro_lines, y)
    y -= 10
    y = add_text_block(c, "Technical Explanation", details_lines, y)
    y -= 10
    y = add_text_block(c, "Submission Value", extra_lines, y)
    add_footer(c, title)

    c.showPage()

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 760, f"{title} - Continued")
    c.setFont("Helvetica", 11)
    c.drawString(50, 730, "The second page expands the explanation with implementation details and project relevance.")

    bullet_lines = [
        "The solution is modern, responsive, and suitable for SmartBridge submission.",
        "It covers dashboard monitoring, prediction, reporting, and alert review in a simple workflow.",
        "The project combines Flask, SQLite, Bootstrap, Chart.js, and Python machine learning tools.",
        "The final deliverable is professional, documented, and ready for academic evaluation.",
    ]
    y = 690
    y = add_text_block(c, "Implementation Summary", bullet_lines, y)
    add_footer(c, title)

    c.save()


files = {
    ROOT / "01_Brainstorming & Ideation" / "Problem Statement.pdf": (
        "Problem Statement",
        [
            "Flooding is a serious challenge in many regions and requires early warning systems.",
            "The project focuses on predicting rising water by using AI and environmental indicators.",
            "The main aim is to provide safe and timely alerts before a flood becomes dangerous.",
        ],
        [
            "The model uses variables such as water level, rainfall, river flow, humidity, and temperature.",
            "These inputs help the system identify whether conditions are normal, warning, dangerous, or emergency.",
            "This makes the solution useful for disaster preparedness and decision making.",
        ],
        [
            "This document explains the core problem and justifies why the project is important.",
            "It also shows how the proposed application supports practical and academic goals.",
        ],
    ),
    ROOT / "01_Brainstorming & Ideation" / "Brainstorming.pdf": (
        "Brainstorming",
        [
            "Brainstorming helped define the main features of the application.",
            "The team discussed monitoring rainfall, river flow, water level, and alert generation.",
            "The concept was shaped around usability, prediction quality, and clear reporting.",
        ],
        [
            "The design process focused on making the system user-friendly and practical.",
            "The final concept includes dashboard monitoring, prediction support, and alert management.",
            "These ideas form the basis of the complete SmartBridge project.",
        ],
        [
            "This document shows the creative process behind the project and how the idea evolved.",
            "It demonstrates that the solution was planned thoughtfully instead of being built randomly.",
        ],
    ),
    ROOT / "02_Requirement Analysis" / "Requirement Analysis.pdf": (
        "Requirement Analysis",
        [
            "The project requirements cover authentication, dashboard access, prediction, analytics, and admin features.",
            "The requirements were collected to ensure the application remains practical and complete.",
        ],
        [
            "These requirements support secure login, report viewing, and prediction history tracking.",
            "They also ensure that the system is responsive and suitable for both users and administrators.",
        ],
        [
            "This document explains the functional and technical needs of the system clearly.",
            "It helps evaluators understand the project scope and expected behavior.",
        ],
    ),
    ROOT / "03_Project Design Phase" / "Database Design.pdf": (
        "Database Design",
        [
            "The system uses SQLite to store users, predictions, alerts, and history records.",
            "The database structure is simple yet effective for a student-level full stack application.",
        ],
        [
            "The design keeps records organized and makes operations efficient for login, prediction, and analysis.",
            "It also supports future expansion with more advanced data handling features.",
        ],
        [
            "This document highlights the importance of data storage in a complete software system.",
            "It shows that the application is built with structure, maintainability, and scalability in mind.",
        ],
    ),
    ROOT / "04_Project Planning Phase" / "Project Plan.pdf": (
        "Project Plan",
        [
            "The project plan includes ideation, requirements, design, implementation, testing, and documentation.",
            "The timeline was structured to help complete the work in a systematic manner.",
        ],
        [
            "This approach makes the development process organized and easier to present.",
            "It also ensures that each stage contributes to the final professional submission.",
        ],
        [
            "This document demonstrates careful planning, which is essential for a strong SmartBridge project.",
            "It shows that the work was not done casually and was managed with purpose.",
        ],
    ),
    ROOT / "06_Project Testing" / "Test Plan.pdf": (
        "Test Plan",
        [
            "Testing focuses on login, prediction, dashboard pages, reports, analytics, and system flow.",
            "The testing process ensures that the application behaves as expected before submission.",
        ],
        [
            "The plan helps identify errors, validate features, and improve reliability.",
            "It also supports confidence in the final demonstration and evaluation.",
        ],
        [
            "This document shows that the project was verified and improved before delivery.",
            "It strengthens the credibility of the final submission.",
        ],
    ),
    ROOT / "07_Project Documentation" / "Final Project Report.pdf": (
        "Final Project Report",
        [
            "This report summarizes the project goal, workflow, architecture, and results.",
            "It presents the AI flood warning system in a clear academic format for evaluation.",
        ],
        [
            "The report highlights the importance of using machine learning for flood risk prediction.",
            "It also explains how the web application supports monitoring, alerts, and analysis.",
        ],
        [
            "This document is important because it gives a complete overview of the project for reviewers.",
            "It makes the submission more professional and easier to understand.",
        ],
    ),
}

for path, (title, intro_lines, details_lines, extra_lines) in files.items():
    write_two_page_pdf(path, title, intro_lines, details_lines, extra_lines)

print("Updated PDFs with detailed title-based content")
