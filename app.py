from flask import Flask, render_template, request, redirect, send_file
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os
import zipfile

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

app = Flask(__name__)

JSON_FILE = "students.json"
WORKSHOP_JSON = "workshop.json"

CERT_FOLDER = "certificates"
ZIP_FILE = "certificates.zip"
WORKSHOP_ZIP = "workshop_certificates.zip"

if not os.path.exists(CERT_FOLDER):
    os.makedirs(CERT_FOLDER)


pdfmetrics.registerFont(TTFont("CasusPro", "fonts/CasusPro.ttf"))
pdfmetrics.registerFont(TTFont("CasusPro-Bold", "fonts/CasusPro-Bold.ttf"))

pdfmetrics.registerFontFamily(
    "CasusPro",
    normal="CasusPro",
    bold="CasusPro-Bold"
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/students")
def view_students():
    if not os.path.exists(JSON_FILE):
        students = []
    else:
        with open(JSON_FILE, "r") as f:
            students = json.load(f)

    return render_template("students.html", students=students)


@app.route("/generate-page")
def generate_page():
    return render_template("generatecertificate.html")

@app.route("/workshop-page")
def workshop_page():
    return render_template("workshopcetificate.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    college = request.form.get("college")
    paper_title = request.form.get("paper_title")
    email = request.form.get("email")

    new_data = {
        "name": name,
        "college": college,
        "paper_title": paper_title,
        "email": email
    }

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_data)

    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return redirect("/form")

@app.route("/workshop-students")
def workshop_students():
    if not os.path.exists(WORKSHOP_JSON):
        students = []
    else:
        with open(WORKSHOP_JSON, "r") as f:
            students = json.load(f)

    return render_template("workshop_students.html", students=students)

@app.route("/generate-workshop-batch/<int:batch>")
def generate_workshop_batch(batch):

    if not os.path.exists(WORKSHOP_JSON):
        return "No workshop data found."

    with open(WORKSHOP_JSON, "r") as f:
        students = json.load(f)

    batch_size = 10
    start = batch * batch_size
    end = start + batch_size
    selected_students = students[start:end]

    if not selected_students:
        return "No more certificates to generate."

    zip_name = f"workshop_certificates_{batch + 1}.zip"

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:

        for student in selected_students:
            name = student["name"]
            college = student["college"]

            safe_name = name.replace(" ", "_")
            pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}_workshop.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage(
                "certificate_template_workshop.jpg",
                0, 0, width, height
            )

            c.setFont("CasusPro", 22)
            c.drawCentredString(width / 2, 400, name)

            style = ParagraphStyle(
                name="WorkshopText",
                fontName="CasusPro",
                fontSize=13,
                leading=30,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has participated in the
<b>ONE DAY WORKSHOP ON
PROBLEM SOLVING AND PROGRAMMING USING PYTHON</b>
organised by <b>DEPARTMENT OF
COMPUTER APPLICATIONS</b> on <b>07/01/2026</b>.
"""

            frame = Frame(
                x1=85,
                y1=160,
                width=width - 180,
                height=210,
                showBoundary=0
            )

            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}_workshop.pdf")

    return send_file(zip_name, as_attachment=True)


@app.route("/generate")
def generate_certificates():

    if not os.path.exists(JSON_FILE):
        return "No student data found."

    with open(JSON_FILE, "r") as f:
        students = json.load(f)

    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zipf:

        for student in students:
            name = student["name"]
            college = student["college"]
            paper = student["paper_title"]

            safe_name = name.replace(" ", "_")
            pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage("certificate_template.jpg", 0, 0, width, height)

            c.setFont("CasusPro", 22)
            c.drawCentredString(width / 2, 400, name)

            style = ParagraphStyle(
                name="CertificateText",
                fontName="CasusPro",
                fontSize=13,
                leading=23,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> and it is selected as the Best Paper in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE
FUTURE"</b> organised by <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> From<b> 05/02/2026  To  06/02/2026</b>
"""

            frame = Frame(
                x1=85,
                y1=170,
                width=width - 180,
                height=210,
                showBoundary=0
            )

            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(ZIP_FILE, as_attachment=True, download_name="certificates.zip")


@app.route("/generate-workshop")
def generate_workshop_certificates():

    if not os.path.exists(WORKSHOP_JSON):
        return "No workshop data found."

    with open(WORKSHOP_JSON, "r") as f:
        students = json.load(f)

    with zipfile.ZipFile(WORKSHOP_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:

        for student in students:
            name = student["name"]
            college = student["college"]

            safe_name = name.replace(" ", "_")
            pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}_workshop.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage("certificate_template_workshop.jpg", 0, 0, width, height)

            c.setFont("CasusPro", 22)
            c.drawCentredString(width / 2, 400, name)

            style = ParagraphStyle(
                name="WorkshopText",
                fontName="CasusPro",
                fontSize=13,
                leading=30,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has participated in the
<b>ONE DAY WORKSHOP ON
PROBLEM SOLVING AND PROGRAMMING USING PYTHON</b>
organised by <b>DEPARTMENT OF
COMPUTER APPLICATIONS</b> on <b>07/01/2026</b>.
"""

            frame = Frame(
                x1=85,
                y1=160,
                width=width - 180,
                height=210,
                showBoundary=0
            )

            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}_workshop.pdf")

    return send_file(
        WORKSHOP_ZIP,
        as_attachment=True,
        download_name="workshop_certificates.zip"
    )



if __name__ == "__main__":
    app.run()
