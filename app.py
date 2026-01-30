from flask import Flask, render_template, request, redirect, send_file
import json
import os
import zipfile

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)


JSON_FILE = "students.json"
CERT_FOLDER = "certificates"
ZIP_FILE = "certificates.zip"

if not os.path.exists(CERT_FOLDER):
    os.makedirs(CERT_FOLDER)



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

            c.drawImage("certificate_template.jpg", 0, 0, width, height)

            c.setFont("Times-Bold", 22)
            c.drawCentredString(width / 2, 420, name)

            x = 100
            y = 360

            c.setFont("Times-Roman", 14)
            c.drawString(x, y, "of ")

            c.setFont("Times-Bold", 14)
            c.drawString(x + 25, y, college)

            c.setFont("Times-Roman", 14)
            c.drawString(
                x + 25 + len(college) * 7,
                y,
                " has presented a paper titled as "
            )

            c.setFont("Times-Bold", 14)
            c.drawString(
                x + 25 + len(college) * 7 + 235,
                y,
                paper
            )

            c.setFont("Times-Roman", 14)
            c.drawString(
                x,
                y - 30,
                "and it is selected as the Best Paper in the"
            )

            c.drawString(
                x,
                y - 60,
                "INTERNATIONAL CONFERENCE ON \"VIKSIT BHARAT 2047: INTEGRATING\""
            )

            c.drawString(
                x,
                y - 90,
                "BUSINESS, TECHNOLOGY AND COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE"
            )

            c.drawString(
                x,
                y - 120,
                "FUTURE organised by DEPARTMENT OF COMPUTER APPLICATIONS"
            )

            c.drawString(
                x,
                y - 150,
                "From 05/02/2026 To 06/02/2026"
            )
            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(
        ZIP_FILE,
        as_attachment=True,
        download_name="certificates.zip"
    )


if __name__ == "__main__":
    app.run(debug=True)
