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
CONFERENCE_PART_JSON="confernceparticipant.json"

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


@app.route("/generate-page")
def generate_page():
    return render_template("generatecertificate.html")

@app.route("/workshop-page")
def workshop_page():
    return render_template("workshopcetificate.html")

@app.route("/submit", methods=["POST"])
def submit():
    new_data = {
        "name": request.form.get("name"),
        "college": request.form.get("college"),
        "paper_title": request.form.get("paper_title"),
        "email": request.form.get("email")
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
    total_students = len(students)
    total_batches = (total_students + batch_size - 1) // batch_size

    if batch >= total_batches:
        batch = 0

    start = batch * batch_size
    end = start + batch_size
    selected_students = students[start:end]

    zip_name = f"workshop_certificates_batch_{batch + 1}.zip"

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for student in selected_students:
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

    response = send_file(zip_name, as_attachment=True)
    response.headers["Refresh"] = "0; url=/workshop-students"
    return response


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

            c.setFont("CasusPro-Bold", 17)
            c.drawCentredString(width / 2, 410, name)

            style = ParagraphStyle(
                name="CertificateText",
                fontName="CasusPro",
                fontSize=13,
                leading=20,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> and it is selected as the Best Paper in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE
FUTURE"</b> organised by <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> From<b> 05/02/2026 To 06/02/2026</b>
"""

            frame = Frame(
                x1=87,
                y1=180,
                width=width - 180,
                height=210,
                showBoundary=0
            )

            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(ZIP_FILE, as_attachment=True, download_name="certificates.zip")


#workshopinte certificate detials adding 

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

#workshopinte students form submission route

@app.route("/workshop-submit", methods=["POST"])
def workshop_submit():
    new_data = {
        "name": request.form.get("student_name"),
        "college": request.form.get("student_college")
    }

    if os.path.exists(WORKSHOP_JSON):
        with open(WORKSHOP_JSON, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_data)

    with open(WORKSHOP_JSON, "w") as f:
        json.dump(data, f, indent=4)

    return redirect("/workshopform")

@app.route("/workshopform")
def workshopform():
    return render_template("workshopform.html")


# ella certificate donwload cheyyan route

@app.route("/download-all-certificates")
def download_all_certificates():
    if not os.path.exists(JSON_FILE):
        return "No student data found."

    with open(JSON_FILE, "r") as f:
        students = json.load(f)

    all_zip = "all_certificates.zip"

    with zipfile.ZipFile(all_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for student in students:
            name = student["name"]
            college = student["college"]
            paper = student["paper_title"]

            safe_name = name.replace(" ", "_")
            pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage("certificate_template.jpg", 0, 0, width, height)

            c.setFont("CasusPro-Bold", 17)
            c.drawCentredString(width / 2, 410, name)

            style = ParagraphStyle(
                name="CertificateText",
                fontName="CasusPro",
                fontSize=13,
                leading=20,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> and it is selected as the Best Paper in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE
FUTURE"</b> organised by <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> From <b>05/02/2026 To 06/02/2026</b>
"""

            frame = Frame(87, 180, width - 180, 210, showBoundary=0)
            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(all_zip, as_attachment=True)

#conference certficatinte all certifcate downloaded page

@app.route('/conferencealldownload')
def conferencealldownload():
    return render_template("conferencealldownload.html")

#dynamic certificate template generating software

@app.route("/generate-dynamic-certificates", methods=["POST"])
def generate_dynamic_certificates():

    if not os.path.exists(JSON_FILE):
        return "No student data found."

    cert_type = request.form.get("cert_type")
    program_name = request.form.get("program_name")
    organized_by = request.form.get("organized_by")
    event_date = request.form.get("event_date")

    coordinators = request.form.getlist("coordinators[]")
    coordinators = [c for c in coordinators if c.strip()]

    with open(JSON_FILE, "r") as f:
        students = json.load(f)

    zip_name = "dynamic_certificates.zip"

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:

        for student in students:
            name = student["name"]
            college = student["college"]
            paper = student.get("paper_title", "")

            safe_name = name.replace(" ", "_")
            pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage("template.jpg", 0, 0, width, height)

            c.setFont("CasusPro-Bold", 18)
            c.drawCentredString(width / 2, 470, "PRESENTATION CERTIFICATE")

            c.setFont("CasusPro", 12)
            c.drawCentredString(width / 2, 445, "This is to certify that")

            c.setFont("CasusPro-Bold", 20)
            c.drawCentredString(width / 2, 415, name)

            style = ParagraphStyle(
                name="CertBody",
                fontName="CasusPro",
                fontSize=12,
                leading=18,
                alignment=TA_JUSTIFY
            )

            if cert_type == "best_paper":
                body_text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> and it is selected as the Best Paper in the
<b>{program_name}</b> organised by
<b>{organized_by}</b>
From <b>{event_date}</b>.
"""
            elif cert_type == "presentation":
                body_text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> in the
<b>{program_name}</b> organised by
<b>{organized_by}</b>
From <b>{event_date}</b>.
"""
            else:
                body_text = f"""
of <b>{college}</b> has actively participated in the
<b>{program_name}</b> organised by
<b>{organized_by}</b>
On <b>{event_date}</b>.
"""

            frame = Frame(85, 200, width - 170, 180, showBoundary=0)
            frame.addFromList([Paragraph(body_text, style)], c)
            c.setFont("CasusPro", 9)

            if len(coordinators) == 2:
                x_positions = [200, 400]
            elif len(coordinators) == 3:
                x_positions = [140, 300, 460]
            else:
                x_positions = []

            for i, coord in enumerate(coordinators):
                c.drawCentredString(x_positions[i], 115, coord)
                c.drawCentredString(x_positions[i], 100, "Coordinator")

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(zip_name, as_attachment=True)


@app.route('/dynamic_event_cert')
def dynamic_event_cert():
    return render_template("Eventcertificatepage.html")

#conference participation certificate template 

@app.route('/conferenceparticipation')
def conferenceparticipation():
    return render_template("conferenceparticipationform.html")


@app.route("/submit-conference", methods=["POST"])
def submit_conference():
    new_data = {
        "name": request.form.get("name"),
        "college": request.form.get("college"),
        "paper_title": request.form.get("paper_title"),
    }

    if os.path.exists(CONFERENCE_PART_JSON):
        with open(CONFERENCE_PART_JSON, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_data)

    with open(CONFERENCE_PART_JSON, "w") as f:
        json.dump(data, f, indent=4)

    return redirect("/conferenceparticipation")

#conference participation certificate download page

@app.route("/download-all-participant-certificates")
def download_all_participant_certificates():
    if not os.path.exists(CONFERENCE_PART_JSON):
        return "No student data found."

    with open(CONFERENCE_PART_JSON, "r") as f:
        students = json.load(f)

    all_zip = "all_conference_participation_certificates.zip"

    with zipfile.ZipFile(all_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for student in students:
            name = student["name"]
            college = student["college"]
            paper = student["paper_title"]

            safe_name = name.replace(" ", "_")
            pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage("participantcertificatefinal.jpg", 0, 0, width, height)

            c.setFont("CasusPro-Bold", 17)
            c.drawCentredString(width / 2, 410, name)

            style = ParagraphStyle(
                name="CertificateText",
                fontName="CasusPro",
                fontSize=13,
                leading=20,
                alignment=TA_JUSTIFY
            )

            text = f"""
of <b>{college}</b> has presented a paper titled as
<b>{paper}</b> and it is selected as the Best Paper in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE
FUTURE"</b> organised by <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> From <b>05/02/2026 To 06/02/2026</b>
"""

            frame = Frame(87, 180, width - 180, 210, showBoundary=0)
            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

    return send_file(all_zip, as_attachment=True)


if __name__ == "__main__":
    app.run()
