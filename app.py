from flask import Flask, render_template, request, redirect, send_file
import json
import os
import zipfile

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
JSON_FILE = "students.json"
CERT_FOLDER = "certificates"
ZIP_FILE = "certificates.zip"

if not os.path.exists(CERT_FOLDER):
    os.makedirs(CERT_FOLDER)

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/generate-page")
def generate_page():
    return render_template("generatecertificate.html")


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

            # -----------------------------
            # BACKGROUND TEMPLATE
            # -----------------------------
            c.drawImage("certificate_template.jpg", 0, 0, width, height)

            # -----------------------------
            # STUDENT NAME (MOVED DOWN)
            # -----------------------------
            c.setFont("Times-Bold", 22)
            c.drawCentredString(width / 2, 400, name)

            # -----------------------------
            # CERTIFICATE PARAGRAPH (JUSTIFIED + BELOW DOTTED LINE)
            # -----------------------------
            style = ParagraphStyle(
                name="CertificateText",
                fontName="Times-Roman",
                fontSize=13,
                leading=19,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> and it is selected as the Best Paper in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE
FUTURE"</b> organised by <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> From 05/02/2026 To 06/02/2026
"""

            frame = Frame(
                x1=95,               # left inside black line
                y1=170,               # pushed DOWN below dotted line
                width=width - 180,    # right boundary
                height=210,           # paragraph height
                showBoundary=0
            )

            frame.addFromList([Paragraph(text, style)], c)

            # -----------------------------
            # SIGNATURE TITLES
            # -----------------------------
            c.setFont("Times-Roman", 11)
           

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(
        ZIP_FILE,
        as_attachment=True,
        download_name="certificates.zip"
    )


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
