#!/usr/bin/env python3
"""
Generate MockMate AWS Project Report as Word document, then convert to PDF.
Follows the exact blueprint format from prompt.txt.
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
import subprocess
import sys
import os

# ============================================================
# CONFIGURATION
# ============================================================
TEAM_MEMBERS = [
    "Dheeraj Moolya (27)",
    "Amey Padwal (31)",
    "Mayuresh Panhalkar (35)"
]

PROJECT_TITLE = "MockMate — AI-Powered Interview Preparation Platform"
SUBTITLE = "AWS Cloud Architecture Implementation Report"

# Figure data from blueprint (adjusted: user's Fig 9 = CloudWatch, not IAM)
FIGURES = [
    (1, "Lambda **Functions** list with all four `mockmate-*` functions", "Lambda functions forming the MockMate backend"),
    (2, "Cognito **Users** list showing your confirmed user", "Cognito user pool with a registered, verified user"),
    (3, "Cognito **App client** page showing no client secret", "Public app client used by the web application"),
    (4, "API Gateway **Routes** page with all four routes", "API routes mapped to Lambda functions"),
    (5, "API Gateway **Attach authorizers to routes** with `cognito` on every route", "JWT authorizer protecting all routes"),
    (6, "Browser showing `{\"message\":\"Unauthorized\"}` at the `/interviews` URL", "Request without a token rejected before reaching Lambda"),
    (7, "DynamoDB table details with the `sessionId` key and the **Indexes** tab showing both indexes Active", "DynamoDB table and global secondary indexes"),
    (8, "DynamoDB **Explore table items** with your report rows", "Interview results stored per session"),
    (9, "CloudWatch **log stream** of one request (START, END, REPORT lines)", "Request logs used for monitoring and debugging"),
    (10, "IAM `mockmate-dynamo` policy JSON (blur the account ID)", "Least-privilege policy limited to one table"),
]

# Screenshot image files (figures 1-9 have actual images; 10-11 are placeholders)
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
FIGURE_IMAGES = {
    1: os.path.join(SCREENSHOT_DIR, "figure_01_lambda_functions.jpg"),
    2: os.path.join(SCREENSHOT_DIR, "figure_02_cognito_users.jpg"),
    3: os.path.join(SCREENSHOT_DIR, "figure_03_cognito_app_client.jpg"),
    4: os.path.join(SCREENSHOT_DIR, "figure_04_api_routes.jpg"),
    5: os.path.join(SCREENSHOT_DIR, "figure_05_api_authorizer.jpg"),
    6: os.path.join(SCREENSHOT_DIR, "figure_06_unauthorized_test.jpg"),
    7: os.path.join(SCREENSHOT_DIR, "figure_07_dynamodb_table.jpg"),
    8: os.path.join(SCREENSHOT_DIR, "figure_08_dynamodb_items.jpg"),
    9: os.path.join(SCREENSHOT_DIR, "figure_09_iam_policy.jpg"),  # Actually CloudWatch screenshot
    # 10: IAM policy - no image yet (placeholder)
    # 11: App report - optional (placeholder)
}

# Services table data (updated figure refs: Fig 9=CloudWatch, Fig 10=IAM)
SERVICES_TABLE = [
    (1, "Amazon Cognito", "User sign-up, login and identity tokens", "User pool, email sign-in, no-secret app client", "Fig. 2, 3"),
    (2, "Amazon API Gateway", "Public HTTPS entry point with token validation", "HTTP API, four routes, JWT authorizer, CORS", "Fig. 4, 5, 6"),
    (3, "AWS Lambda", "Interview logic: start, answer, report, history", "Python 3.12, 512 MB, 30 s timeout", "Fig. 1"),
    (4, "Amazon DynamoDB", "Stores sessions, answers and reports", "On-demand table, `userId-index`, `sessionId-index`", "Fig. 7, 8"),
    (5, "AWS IAM", "Controls what Lambda may access", "Execution role, inline policy on one table", "Fig. 10"),
    (6, "Amazon CloudWatch", "Logs and metrics for every function run", "Per-function log groups", "Fig. 9"),
]

# AWS Architecture details
AWS_ARCH = {
    "Frontend Hosting": {
        "Service": "AWS Amplify (Next.js 16 app)",
        "Build Config": "amplify.yml at root + frontend/amplify.yml",
        "Build Command": "npm ci && npm run build",
        "Artifact Directory": ".next (Next.js static export)",
        "Cache": "node_modules/**/*",
        "Region": "us-east-1 (from API Gateway URL)",
    },
    "Authentication": {
        "User Pool ID": "us-east-1_080jB5zPv",
        "App Client ID": "275ivahauujacfd51r52ssv1v6",
        "Hosted UI Domain": "Not configured (optional)",
        "OAuth Flows": "Ready for implementation",
        "Region": "us-east-1",
    },
    "Backend API": {
        "API Endpoint": "https://m8o2rs04vc.execute-api.us-east-1.amazonaws.com",
        "Protocol": "REST API",
        "Stage": "Implied /prod (not explicit in URL)",
        "Local Mock": "mock-server.js on http://localhost:3001",
        "Endpoints": "/interview/start, /interview/answer, /interview/report, /interviews",
    },
}

# Frontend dependencies
FRONTEND_DEPS = {
    "aws-amplify": "^6.22.2",
    "@aws-amplify/ui-react": "^6.15.7",
}

# Key config files
CONFIG_FILES = [
    ("amplify.yml (root)", "Amplify app build spec with appRoot: frontend"),
    ("frontend/amplify.yml", "Frontend-specific build phases"),
    ("frontend/.env.local", "Production Cognito + API Gateway config"),
    ("frontend/.env.local.example", "Template for local development"),
    ("mock-server.js", "Local Lambda mock for development"),
]

# Observations
OBSERVATIONS = [
    ("Amplify Config", "✅ Dual config", "Root + frontend both have amplify.yml — root references appRoot: frontend"),
    ("Cognito Config", "✅ Hardcoded in .env.local", "Pool ID & Client ID committed — should use Amplify env vars in production"),
    ("API Gateway URL", "✅ Hardcoded", "Same concern — move to Amplify environment variables"),
    ("Local Dev", "✅ Mock server", "mock-server.js simulates Lambda locally on port 3001"),
    ("MediaPipe", "✅ Local assets", "WASM models in public/mediapipe/ — no external AWS dependency"),
]

# Implementation steps (updated figure refs: Fig 9=CloudWatch, Fig 10=IAM)
IMPL_STEPS = [
    ("8.1", "Lambda Functions", "Four Lambda functions (`mockmate-start`, `mockmate-answer`, `mockmate-report`, `mockmate-history`) implement the interview workflow. Each function is written in Python 3.12 with 512 MB memory and 30-second timeout.", "Fig. 1"),
    ("8.2", "Cognito User Pool", "A Cognito user pool handles authentication with email-based sign-in. The app client is configured without a client secret for secure SPA integration. A test user is created and verified.", "Fig. 2, 3"),
    ("8.3", "API Routes and Authorizer", "API Gateway HTTP API exposes four routes mapped to Lambda functions. A JWT authorizer validates Cognito tokens on every route. CORS is configured for the Amplify frontend domain.", "Fig. 4, 5"),
    ("8.4", "Security Test", "A direct request to `/interviews` without an Authorization header returns `{\"message\":\"Unauthorized\"}`, confirming the authorizer blocks unauthenticated traffic before it reaches Lambda.", "Fig. 6"),
    ("8.5", "DynamoDB", "A single on-demand table stores sessions, answers, and reports. Two global secondary indexes (`userId-index`, `sessionId-index`) enable efficient query patterns for history and report retrieval.", "Fig. 7, 8"),
    ("8.6", "IAM Policy", "The Lambda execution role carries an inline policy (`mockmate-dynamo`) granting least-privilege access (PutItem, GetItem, Query, Scan) only on the MockMate table.", "Fig. 10"),
    ("8.7", "CloudWatch Monitoring", "Each Lambda function writes to its own CloudWatch log group. Log streams capture START, END, and REPORT lines for every invocation, enabling debugging and performance monitoring.", "Fig. 9"),
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def set_cell_shading(cell, color):
    """Set background color of a table cell."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading_styled(doc, text, level=1):
    """Add a heading with consistent styling."""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)  # Dark slate
    return heading


def add_body_text(doc, text, bold=False, italic=False, size=11):
    """Add a paragraph with consistent body styling."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = 'Calibri'
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.space_before = Pt(2)
    return p


def add_bullet(doc, text, level=0):
    """Add a bullet point."""
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 1.27)
    return p


def create_table(doc, headers, rows, col_widths=None):
    """Create a formatted table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_shading(cell, '1F2937')

    # Data rows
    for r, row_data in enumerate(rows):
        for c, cell_text in enumerate(row_data):
            cell = table.rows[r + 1].cells[c]
            cell.text = str(cell_text)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(10)
            if r % 2 == 0:
                set_cell_shading(cell, 'F3F4F6')

    # Set column widths if provided
    if col_widths:
        for row in table.rows:
            for i, width in enumerate(col_widths):
                row.cells[i].width = Inches(width)

    return table


def add_figure_placeholder(doc, fig_num, screenshot_desc, caption):
    """Add a figure placeholder with caption."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"[ INSERT SCREENSHOT HERE — Figure {fig_num} ]")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.font.name = 'Calibri'

    # Caption
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(f"Figure {fig_num}: {caption}")
    run.bold = True
    run.font.size = Pt(10)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    cap.paragraph_format.space_after = Pt(12)

    return p


def add_figure_with_image(doc, fig_num, image_path, caption, max_width_inches=6.0):
    """Add a figure with actual image embedded."""
    if not os.path.exists(image_path):
        print(f"⚠️  Image not found: {image_path} — using placeholder for Figure {fig_num}")
        return add_figure_placeholder(doc, fig_num, "", caption)

    # Add image
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(image_path, width=Inches(max_width_inches))

    # Caption
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(f"Figure {fig_num}: {caption}")
    run.bold = True
    run.font.size = Pt(10)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    cap.paragraph_format.space_after = Pt(12)

    return p


# ============================================================
# DOCUMENT BUILDING
# ============================================================
def build_document():
    doc = Document()

    # Page setup
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

    # Default style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # ============================================================
    # TITLE PAGE
    # ============================================================
    for _ in range(6):
        doc.add_paragraph()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(PROJECT_TITLE)
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
    run.font.name = 'Calibri'

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run(SUBTITLE)
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)
    run.font.name = 'Calibri'

    doc.add_paragraph()
    doc.add_paragraph()

    # Team members
    team_heading = doc.add_paragraph()
    team_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = team_heading.add_run("Team Members")
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    for member in TEAM_MEMBERS:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(member)
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    doc.add_paragraph()
    doc.add_paragraph()

    # Date
    date_p = doc.add_paragraph()
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = date_p.add_run("November 2026")
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # Page break
    doc.add_page_break()

    # ============================================================
    # PROJECT SUBMISSION DETAILS
    # ============================================================
    add_heading_styled(doc, "Project Submission Details", level=1)

    submission_data = [
        ("Project Name", "MockMate"),
        ("Domain", "Cloud Computing / AI-Powered EdTech"),
        ("Cloud Platform", "Amazon Web Services (AWS)"),
        ("Region", "us-east-1 (N. Virginia)"),
        ("Frontend Framework", "Next.js 16 (React 19)"),
        ("Backend Runtime", "AWS Lambda (Python 3.12)"),
        ("Authentication", "Amazon Cognito"),
        ("API Layer", "Amazon API Gateway (HTTP API)"),
        ("Database", "Amazon DynamoDB (On-Demand)"),
        ("Monitoring", "Amazon CloudWatch Logs"),
        ("CI/CD", "AWS Amplify (Git-based deployment)"),
        ("Team Members", ", ".join(TEAM_MEMBERS)),
    ]

    create_table(doc, ["Attribute", "Details"], submission_data, col_widths=[2.5, 4.0])
    doc.add_paragraph()

    # ============================================================
    # INTRODUCTION
    # ============================================================
    add_heading_styled(doc, "Introduction", level=1)
    add_body_text(doc,
        "MockMate is an AI-powered interview preparation platform that simulates realistic technical interviews "
        "using generative AI for question generation, answer evaluation, and detailed performance reporting. "
        "The platform leverages a serverless architecture on AWS to deliver a scalable, cost-effective, and "
        "secure solution for candidates practicing for software engineering, data science, and product management roles."
    )
    add_body_text(doc,
        "This report documents the AWS cloud architecture, implementation steps, and service configurations "
        "used to deploy MockMate as a production-ready application."
    )

    # ============================================================
    # PROBLEM STATEMENT
    # ============================================================
    add_heading_styled(doc, "Problem Statement", level=1)
    add_body_text(doc,
        "Candidates preparing for technical interviews lack access to realistic, adaptive interview simulations "
        "that provide structured feedback. Existing solutions are either static question banks, expensive "
        "mock interview services, or require manual setup. There is a need for an automated, cloud-native "
        "platform that:"
    )
    add_bullet(doc, "Generates role- and difficulty-appropriate interview questions dynamically")
    add_bullet(doc, "Evaluates answers using AI with structured scoring (technical accuracy, communication, problem-solving)")
    add_bullet(doc, "Captures body language metrics via webcam (eye contact, posture, gestures, attention)")
    add_bullet(doc, "Produces comprehensive reports with category scores and actionable recommendations")
    add_bullet(doc, "Scales automatically with demand and costs near-zero when idle")
    add_bullet(doc, "Secures user data with authentication and authorization")

    # ============================================================
    # PROPOSED SOLUTION & PROJECT DESCRIPTION
    # ============================================================
    add_heading_styled(doc, "Proposed Solution and Project Description", level=1)
    add_body_text(doc,
        "MockMate is implemented as a full-stack serverless application on AWS. The frontend is a Next.js 16 "
        "application hosted on AWS Amplify with automatic CI/CD from Git. The backend consists of four Lambda "
        "functions exposed via Amazon API Gateway HTTP API, protected by a Cognito JWT authorizer. Data is "
        "stored in a single DynamoDB table with two global secondary indexes. Authentication uses Amazon Cognito "
        "with email-based sign-in and a public app client (no client secret) suitable for SPA deployment."
    )
    add_body_text(doc,
        "The interview workflow: a user starts a session (role, difficulty, language) → answers 5 questions "
        "sequentially → receives AI evaluation per answer → body language metrics are captured via MediaPipe "
        "Face Mesh in the browser → a final report is generated with overall score, category breakdown, "
        "body language summary, and AI-generated recommendations. All data persists in DynamoDB for history "
        "and analytics."
    )

    # ============================================================
    # CLOUD PLATFORM AND SERVICES USED
    # ============================================================
    add_heading_styled(doc, "Cloud Platform and Services Used", level=1)
    add_body_text(doc,
        "The project is deployed exclusively on Amazon Web Services in the us-east-1 (N. Virginia) region. "
        "The following table summarizes the six core AWS services, their purpose, and key configuration."
    )

    # Services table (expanded version for this section)
    services_detailed = [
        ("Amazon Cognito", "User authentication & identity tokens", "User pool (email sign-in), public app client (no secret), JWT tokens"),
        ("Amazon API Gateway", "Public HTTPS entry point, request routing, auth", "HTTP API, 4 routes, JWT authorizer, CORS enabled"),
        ("AWS Lambda", "Serverless compute for interview logic", "4 functions, Python 3.12, 512 MB, 30 s timeout, environment variables"),
        ("Amazon DynamoDB", "NoSQL storage for sessions, answers, reports", "On-demand billing, PK=sessionId, GSI1=userId, GSI2=sessionId"),
        ("AWS IAM", "Fine-grained permissions for Lambda", "Execution role + inline policy (mockmate-dynamo) scoped to one table"),
        ("Amazon CloudWatch", "Observability: logs & metrics", "Per-function log groups, structured JSON logging, metric filters"),
        ("AWS Amplify", "Frontend hosting & CI/CD", "Next.js 16 build, auto-deploy on git push, custom domain support"),
    ]
    create_table(doc, ["Service", "Purpose in Project", "Key Configuration"], services_detailed, col_widths=[1.8, 2.2, 3.5])
    doc.add_paragraph()

    # ============================================================
    # AWS ARCHITECTURE OVERVIEW (from prompt.txt)
    # ============================================================
    add_heading_styled(doc, "AWS Architecture Overview", level=1)

    # Frontend Hosting
    add_heading_styled(doc, "Frontend Hosting: AWS Amplify", level=2)
    fe_data = [[k, v] for k, v in AWS_ARCH["Frontend Hosting"].items()]
    create_table(doc, ["Aspect", "Configuration"], fe_data, col_widths=[2.0, 4.5])
    doc.add_paragraph()

    # Authentication
    add_heading_styled(doc, "Authentication: Amazon Cognito", level=2)
    auth_data = [[k, v] for k, v in AWS_ARCH["Authentication"].items()]
    create_table(doc, ["Setting", "Value"], auth_data, col_widths=[2.0, 4.5])
    doc.add_paragraph()

    # Backend API
    add_heading_styled(doc, "Backend API: API Gateway + Lambda", level=2)
    api_data = [[k, v] for k, v in AWS_ARCH["Backend API"].items()]
    create_table(doc, ["Aspect", "Configuration"], api_data, col_widths=[2.0, 4.5])
    doc.add_paragraph()

    # Frontend Dependencies
    add_heading_styled(doc, "Frontend AWS Dependencies", level=2)
    dep_rows = [[k, v] for k, v in FRONTEND_DEPS.items()]
    create_table(doc, ["Package", "Version"], dep_rows, col_widths=[2.5, 1.5])
    doc.add_paragraph()

    # Key Config Files
    add_heading_styled(doc, "Key Configuration Files", level=2)
    create_table(doc, ["File", "Purpose"], CONFIG_FILES, col_widths=[2.5, 4.0])
    doc.add_paragraph()

    # Observations
    add_heading_styled(doc, "Observations & Recommendations", level=2)
    create_table(doc, ["Item", "Status", "Note"], OBSERVATIONS, col_widths=[1.8, 1.5, 3.2])
    doc.add_paragraph()

    # ============================================================
    # IMPLEMENTATION STEPS (with figure placeholders)
    # ============================================================
    add_heading_styled(doc, "Implementation Steps", level=1)
    add_body_text(doc,
        "Each implementation step below corresponds to a figure (screenshot) that demonstrates the "
        "completed configuration. Figures 1–10 are referenced throughout."
    )

    for step_num, title, description, fig_ref in IMPL_STEPS:
        add_heading_styled(doc, f"{step_num} {title}", level=2)
        add_body_text(doc, description)
        add_body_text(doc, f"Evidence: {fig_ref}", italic=True, size=10)
        doc.add_paragraph()

    # ============================================================
    # FIGURES SECTION (with embedded screenshots for 1-9)
    # ============================================================
    add_heading_styled(doc, "Figures (Screenshots)", level=1)
    add_body_text(doc,
        "Figures 1–9 below are embedded from actual AWS Console screenshots (N. Virginia region). "
        "Figures 10–11 are placeholders for CloudWatch logs and the application report screen."
    )
    doc.add_paragraph()

    for fig_num, screenshot_desc, caption in FIGURES:
        add_heading_styled(doc, f"Figure {fig_num}", level=3)
        if fig_num in FIGURE_IMAGES:
            # Embed actual image for figures 1-9
            add_figure_with_image(doc, fig_num, FIGURE_IMAGES[fig_num], caption)
        else:
            # Placeholder for figures 10-11
            add_body_text(doc, f"Capture: {screenshot_desc}", italic=True, size=10)
            add_figure_placeholder(doc, fig_num, screenshot_desc, caption)

    # Optional Fig 11
    add_heading_styled(doc, "Figure 11 (Optional)", level=3)
    add_body_text(doc, "Capture: Application report screen showing end-to-end result", italic=True, size=10)
    add_figure_placeholder(doc, 11, "App report screen with overall score, category breakdown, and AI summary", "MockMate interview report — end-to-end result")

    doc.add_page_break()

    # ============================================================
    # SERVICES TABLE (blueprint format)
    # ============================================================
    add_heading_styled(doc, "Services Mapping Table", level=1)
    add_body_text(doc,
        "This table maps each AWS service to its purpose, key configuration, and the figure(s) that provide evidence."
    )
    create_table(doc, ["Sr. No.", "Service", "Purpose in the Project", "Key Configuration", "Evidence"], SERVICES_TABLE, col_widths=[0.6, 1.3, 1.8, 2.0, 1.0])
    doc.add_paragraph()

    # ============================================================
    # CONCLUSION
    # ============================================================
    add_heading_styled(doc, "Conclusion", level=1)
    add_body_text(doc,
        "MockMate demonstrates a complete serverless architecture on AWS, combining authentication (Cognito), "
        "API management (API Gateway), compute (Lambda), database (DynamoDB), security (IAM), observability "
        "(CloudWatch), and frontend hosting (Amplify) into a cohesive, production-ready interview preparation platform."
    )
    add_body_text(doc,
        "The implementation follows AWS Well-Architected principles:"
    )
    add_bullet(doc, "Security: JWT authorizer on all routes, least-privilege IAM, no secrets in client code")
    add_bullet(doc, "Reliability: Stateless Lambda functions, on-demand DynamoDB, automatic retries")
    add_bullet(doc, "Performance: Edge-hosted frontend via Amplify CDN, low-latency Lambda, efficient DynamoDB indexes")
    add_bullet(doc, "Cost Optimization: Pay-per-use for all services, near-zero idle cost, no provisioned capacity")
    add_bullet(doc, "Operational Excellence: Structured CloudWatch logs, infrastructure as code (Amplify config), automated CI/CD")
    add_body_text(doc,
        "Future enhancements include: Cognito Hosted UI for OAuth flows, custom domain with Route 53, "
        "X-Ray tracing for distributed request tracking, and S3 + CloudFront for MediaPipe model hosting."
    )

    return doc


def convert_to_pdf(docx_path, pdf_path):
    """Convert DOCX to PDF using LibreOffice or pandoc."""
    # Try LibreOffice first
    try:
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', os.path.dirname(pdf_path), docx_path
        ], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            # LibreOffice outputs with same basename
            generated = os.path.join(os.path.dirname(pdf_path), os.path.basename(docx_path).replace('.docx', '.pdf'))
            if os.path.exists(generated) and generated != pdf_path:
                os.rename(generated, pdf_path)
            print(f"✅ PDF generated via LibreOffice: {pdf_path}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try pandoc
    try:
        result = subprocess.run([
            'pandoc', docx_path, '-o', pdf_path
        ], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✅ PDF generated via pandoc: {pdf_path}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("⚠️  Could not convert to PDF automatically.")
    print("   Install LibreOffice or pandoc, or convert manually:")
    print(f"   libreoffice --headless --convert-to pdf {docx_path}")
    print(f"   # or")
    print(f"   pandoc {docx_path} -o {pdf_path}")
    return False


def main():
    print("📄 Building MockMate AWS Project Report...")

    doc = build_document()

    # Save DOCX
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docx_path = os.path.join(base_dir, "MockMate_AWS_Project_Report.docx")
    pdf_path = os.path.join(base_dir, "MockMate_AWS_Project_Report.pdf")

    doc.save(docx_path)
    print(f"✅ Word document saved: {docx_path}")

    # Convert to PDF
    print("🔄 Converting to PDF...")
    convert_to_pdf(docx_path, pdf_path)

    print("\n📋 Next steps:")
    print("1. Open the .docx file and replace each [INSERT SCREENSHOT HERE] placeholder with actual screenshots")
    print("2. Re-save and convert to PDF, or use the generated PDF as a template")
    print(f"3. Final files: {docx_path} and {pdf_path}")


if __name__ == "__main__":
    main()