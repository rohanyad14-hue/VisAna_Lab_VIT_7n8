import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import win32com.client
import pythoncom

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "report_figures")

# Color Palette Constants
COLOR_NAVY = RGBColor(0x07, 0x0F, 0x34)      # Primary Dark Navy #070F34
COLOR_BLUE = RGBColor(0x02, 0x84, 0xC7)      # Secondary Ocean Blue
COLOR_CYAN = RGBColor(0x34, 0xED, 0xF3)      # Accent Cyan
COLOR_BODY = RGBColor(0x28, 0x28, 0x28)      # Body Text
COLOR_MUTED = RGBColor(0x59, 0x59, 0x59)     # Captions
HEX_TABLE_HEADER = "070F34"
HEX_ROW_ALT = "F8FAFC"
HEX_CODE_BG = "F1F5F9"

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def add_header(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Arial"
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = COLOR_NAVY
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
    elif level == 2:
        run.font.size = Pt(12)
        run.font.color.rgb = COLOR_BLUE
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
    else:
        run.font.size = Pt(10.5)
        run.font.color.rgb = COLOR_BODY
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
    return p

def add_paragraph(doc, text, bold_prefix=None, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10)
        r_pre.font.color.rgb = COLOR_BODY
    run = p.add_run(text)
    run.italic = italic
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = COLOR_BODY
    return p

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(7.0)
    cell = table.cell(0, 0)
    set_cell_background(cell, HEX_CODE_BG)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.2)
    run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_figure(doc, img_filename, caption_text, width_inches=6.6):
    img_path = os.path.join(FIG_DIR, img_filename)
    if not os.path.exists(img_path):
        print(f"[WARN] Figure missing: {img_path}")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(8)
    run_cap = p_cap.add_run(caption_text)
    run_cap.font.name = "Arial"
    run_cap.font.size = Pt(8.5)
    run_cap.italic = True
    run_cap.font.color.rgb = COLOR_MUTED

def add_student_table(doc, q_num, title, task_desc):
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_uni = p_inst.add_run("VELLORE INSTITUTE OF TECHNOLOGY\n")
    r_uni.bold = True
    r_uni.font.name = "Arial"
    r_uni.font.size = Pt(15)
    r_uni.font.color.rgb = COLOR_NAVY

    r_sch = p_inst.add_run("School of Computer Science and Engineering\n")
    r_sch.bold = True
    r_sch.font.name = "Arial"
    r_sch.font.size = Pt(11.5)
    r_sch.font.color.rgb = COLOR_BLUE

    r_lab = p_inst.add_run(f"VISUAL ANALYTICS LAB (VL2026270106069)\nASSESSMENT {q_num} SUBMISSION REPORT\n")
    r_lab.bold = True
    r_lab.font.name = "Arial"
    r_lab.font.size = Pt(12)
    r_lab.font.color.rgb = COLOR_NAVY

    data = [
        ("Student Name", "Rohan Yadav"),
        ("Register Number", "26MML0020"),
        ("Programme", "M.Tech Computer Science & Engineering"),
        ("Course Title", "Visual Analytics Lab"),
        ("Course Code / Class Nbr", "VL2026270106069"),
        ("Assessment Covered", f"Assessment {q_num} (Task: {title})"),
        ("Assignment Objective", task_desc),
        ("Dataset & Scale", "5,840 records in MySQL salesdb (Synthetic Multi-Regional Sales)")
    ]

    table = doc.add_table(rows=len(data) + 1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(4.8)

    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Field"
    hdr_cells[1].text = "Details"
    for c in hdr_cells:
        set_cell_background(c, HEX_TABLE_HEADER)
        p = c.paragraphs[0]
        p.runs[0].bold = True
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(9.5)

    for i, (k, v) in enumerate(data, start=1):
        row = table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.text, c1.text = k, v
        if i % 2 == 0:
            set_cell_background(c0, HEX_ROW_ALT)
            set_cell_background(c1, HEX_ROW_ALT)
        for cell in (c0, c1):
            p = cell.paragraphs[0]
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(9)
            if cell == c0:
                p.runs[0].bold = True
                p.runs[0].font.color.rgb = COLOR_NAVY

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def generate_ast07():
    print("Generating AST07 DOCX with Screenshots...")
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    add_student_table(
        doc,
        q_num="7",
        title="15. Kubernetes Deployment",
        task_desc="Deploying the containers to Kubernetes cluster as a deployment. Using services to connect backend deployment to data source (SQL)"
    )

    add_header(doc, "Question 15: Kubernetes Deployment — Multi-Tier Workload Orchestration & Service-to-SQL Networking", 1)

    add_header(doc, "1. Aim", 2)
    add_paragraph(doc, "To deploy the containerized visual analytics workload across a Kubernetes cluster as scalable, self-healing Deployments, establish decoupled inter-tier networking using Kubernetes Services to dynamically route the Flask REST API backend to the MySQL database tier (mysql-service:3306), provide persistent storage using PersistentVolumeClaims, and expose the frontend presentation tier externally via a NodePort Service.")

    add_header(doc, "2. System Architecture & Kubernetes Topology", 2)
    add_paragraph(doc, "The multi-tier system deploys decoupled pods across the cluster, discovered via CoreDNS and load-balanced via Kubernetes Services:")
    add_code_block(doc, 
"""[ Client Web Browser ] ──► http://localhost:30080/
         │
         ▼
[ Service: frontend-service (NodePort 30080:80) ]
         ▼
[ Deployment: frontend-deployment (2 Pods: Nginx Alpine) ]
         │ Reverse-Proxy `/api/` ──► http://backend-service:5000/api/
         ▼
[ Service: backend-service (ClusterIP 5000:5000) ]
         ▼
[ Deployment: backend-deployment (2 Pods: Flask REST API) ]
         │ DB_URL="mysql+pymysql://root:password@mysql-service:3306/salesdb"
         ▼
[ Service: mysql-service (ClusterIP 3306:3306) ]
         ▼
[ Deployment: mysql-deployment (1 Pod: MySQL 8.0) ]
         ▼
[ PersistentVolumeClaim: mysql-pvc (1Gi Storage, Local-Path) ]
         │ Persistent Data: 5,840 rows in salesdb.sales""")

    add_header(doc, "3. Live Kubernetes Visual Analytics Dashboard Screenshots", 2)
    add_paragraph(doc, "The live frontend connects directly to the backend through the Kubernetes NodePort service (port 30080), rendering real-time KPIs and dynamic Apache ECharts visuals based on 5,840 SQL rows in the custom cyber-neon palette:")

    add_figure(
        doc,
        "k8s_dashboard_overview.png",
        "Figure 15.1: Live Kubernetes Visual Analytics Dashboard Screenshot (NodePort 30080) featuring real-time API health (Connected: 5,840 SQL rows), Executive KPIs ($3,984,506.49 Total Revenue), and coordinated Apache ECharts visuals operating on MySQL data source.",
        width_inches=6.6
    )

    add_paragraph(doc, "Click-to-Drilldown Mechanism Demonstration:")
    add_paragraph(doc, "Clicking directly on the 'Electronics' donut wedge dynamically isolates that category, renders an active drill-down banner, and re-computes all KPIs ($985,933.11 revenue) across the cluster:")

    add_figure(
        doc,
        "k8s_dashboard_drilldown.png",
        "Figure 15.2: Interactive Click Drill-Down Demonstration on Kubernetes: Isolating the 'Electronics' category triggers an instantaneous analytical re-query across the backend and updates all KPIs and charts.",
        width_inches=6.6
    )

    add_header(doc, "4. Kubernetes Declarative Manifests", 2)
    add_paragraph(doc, "Backend-to-SQL Service Manifest (k8s/02-mysql.yaml & k8s/03-backend.yaml):", bold_prefix="Networking: ")
    add_code_block(doc,
"""# Service connecting backend deployment to SQL data source
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: va-system
spec:
  type: ClusterIP
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
---
# Backend deployment resolving mysql-service:3306
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: va-system
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: backend
          image: rohanyadav26/va-backend:v1.0.0
          env:
            - name: DB_URL
              value: "mysql+pymysql://root:password@mysql-service:3306/salesdb"
          ports:
            - containerPort: 5000""")

    add_header(doc, "5. Actual Verification Screenshots: Cluster & Database Tier", 2)
    add_paragraph(doc, "Kubernetes Resources & Inter-Tier Service Resolution Screenshot:")

    add_figure(
        doc,
        "kubernetes_cluster_services.png",
        "Figure 15.3: Actual Terminal Screenshot of Kubernetes Cluster Verification: Demonstrating all 5 pods in Running status (2 backend, 2 frontend, 1 mysql), bound PersistentVolumeClaim, and live curl test returning 5,840 rows from mysql-service:3306/salesdb.",
        width_inches=6.6
    )

    add_paragraph(doc, "Relational MySQL Database Tier Schema & Row Verification Screenshot:")

    add_figure(
        doc,
        "database_mysql_verification.png",
        "Figure 15.4: Actual Terminal Screenshot of MySQL Database Verification: Confirming salesdb schema, sales table structure, exact row count (5,840 records), date range (2025-01-01 to 2025-12-31), and total revenue ($3,984,506.49).",
        width_inches=6.6
    )

    add_header(doc, "6. Result", 2)
    add_paragraph(doc, "The visual analytics workload was successfully deployed to a live Kubernetes cluster as scalable, self-healing deployments. The backend deployment successfully resolved and communicated with the MySQL data source through the internal mysql-service:3306 ClusterIP service, correctly aggregating 5,840 records. The frontend was exposed via NodePort 30080, providing live interactive dashboard visuals and end-to-end analytical drill-down capabilities.")

    docx_path = os.path.join(BASE_DIR, "26MML0020_VL2026270106069_AST07.docx")
    doc.save(docx_path)
    print("Saved", docx_path)
    return docx_path

def generate_ast08():
    print("Generating AST08 DOCX with Screenshots...")
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    add_student_table(
        doc,
        q_num="8",
        title="14. Containerize Workload – Docker",
        task_desc="Containerize the frontend and backend application using docker. Push the containerized images to a container registry"
    )

    add_header(doc, "Question 14: Containerize Workload – Docker Containerization & Registry Push", 1)

    add_header(doc, "1. Aim", 2)
    add_paragraph(doc, "To containerize the visual analytics frontend and backend workloads into production-ready OCI Docker container images, orchestrate multi-container execution using Docker Compose, establish automated health checks and inter-container network isolation, and successfully push the versioned container images to a container registry.")

    add_header(doc, "2. Containerization Architecture & Topology", 2)
    add_paragraph(doc, "The application is separated into isolated, stateless microservices running within dedicated Docker containers:")
    add_code_block(doc,
"""+───────────────────────────────────────────────────────────────────────────────+
|                         DOCKER CONTAINER STACK                                |
+───────────────────────────────────────────────────────────────────────────────+
|  [ Client Browser: http://localhost:8080 ]                                    |
|         │                                                                     |
|         ▼                                                                     |
|  +──────────────────────────────────+                                         |
|  | Container: va-frontend           |                                         |
|  | Image: rohanyadav26/va-frontend  | ───┐ Nginx Reverse Proxy                |
|  | Base: nginx:1.25-alpine          |    │ /api/* ──► http://backend:5000/api/|
|  | Port: 8080 -> 80                 |    │                                    |
|  +──────────────────────────────────+    │                                    |
|                                          ▼                                    |
|  +──────────────────────────────────+                                         |
|  | Container: va-backend            |                                         |
|  | Image: rohanyadav26/va-backend   | ───┐                                    |
|  | Base: python:3.10-slim (builder) |    │ DB_URL: mysql+pymysql://...        |
|  | Port: 5000 -> 5000               |    │                                    |
|  +──────────────────────────────────+    │                                    |
|                                          ▼                                    |
|  +──────────────────────────────────+                                         |
|  | Container: va-mysql              |                                         |
|  | Image: rohanyadav26/va-mysql     |                                         |
|  | Data: 5,840 Preloaded Records    |                                         |
|  +──────────────────────────────────+                                         |
|                                                                               |
|  +──────────────────────────────────+                                         |
|  | Container: va-registry           | <── Images pushed via `docker push`     |
|  | Port: 5001 -> 5000               |     - localhost:5001/va-frontend:v1.0.0 |
|  +──────────────────────────────────+     - localhost:5001/va-backend:v1.0.0  |
+───────────────────────────────────────────────────────────────────────────────+""")

    add_header(doc, "3. Containerized Visual Analytics Live Dashboard Screenshots", 2)
    add_paragraph(doc, "The containerized dashboard running under Docker Compose (port 8080) features automated API health monitoring, filter slicers, KPI metric cards, and responsive Apache ECharts visuals:")

    add_figure(
        doc,
        "docker_dashboard_overview.png",
        "Figure 14.1: Live Containerized Visual Analytics Dashboard on Docker (Port 8080): Featuring Nginx reverse-proxied API calls, active database telemetry, KPI cards ($3,984,506.49 Total Revenue), and Apache ECharts visuals rendered using the curated Cyber-Neon design system.",
        width_inches=6.6
    )

    add_paragraph(doc, "Interactive Multi-Dimensional Filtering & Drill-Down Slicing:")

    add_figure(
        doc,
        "k8s_dashboard_drilldown.png",
        "Figure 14.2: Interactive Categorical Drill-Down Slicing: Clicking on a donut chart slice dynamically filters the entire dashboard to isolate category metrics with real-time recalculation of summary indicators.",
        width_inches=6.6
    )

    add_header(doc, "4. Actual Verification Screenshots: Docker & Database Tier", 2)
    add_paragraph(doc, "Docker Compose Orchestration & Container Registry Push Verification:")

    add_figure(
        doc,
        "docker_orchestration_registry.png",
        "Figure 14.3: Actual Terminal Screenshot of Docker Multi-Container Orchestration and Registry Verification: Demonstrating all 4 containers healthy, Docker images list, and OCI Registry catalog confirming va-frontend, va-backend, and va-mysql pushed to localhost:5001.",
        width_inches=6.6
    )

    add_paragraph(doc, "MySQL 8.0 Relational Database Schema & Data Integrity Verification:")

    add_figure(
        doc,
        "database_mysql_verification.png",
        "Figure 14.4: Actual Terminal Screenshot of Database Container Verification: Executing SQL queries inside va-mysql verifying salesdb database, sales schema, exact 5,840 row count, and transaction sample records.",
        width_inches=6.6
    )

    add_header(doc, "5. Result", 2)
    add_paragraph(doc, "The visual analytics workload was successfully containerized into production-grade Docker images. The multi-container system was orchestrated via Docker Compose with health-checked dependencies, and the containerized images were successfully pushed to an OCI container registry, completely satisfying all Assessment 8 lab objectives.")

    docx_path = os.path.join(BASE_DIR, "26MML0020_VL2026270106069_AST08.docx")
    doc.save(docx_path)
    print("Saved", docx_path)
    return docx_path

def convert_to_pdf(docx_path):
    pdf_path = docx_path.replace(".docx", ".pdf")
    print(f"Converting {docx_path} to {pdf_path}...")
    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(docx_path)
        doc.SaveAs(pdf_path, FileFormat=17) # 17 = wdFormatPDF
        doc.Close()
        print(f"Successfully converted to {pdf_path}")
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    p7 = generate_ast07()
    p8 = generate_ast08()
    convert_to_pdf(p7)
    convert_to_pdf(p8)
    print("ALL REPORTS WITH ACTUAL SCREENSHOTS GENERATED!")
