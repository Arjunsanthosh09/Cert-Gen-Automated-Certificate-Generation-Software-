from flask import Flask, render_template, request, redirect, send_file
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os
import zipfile
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import io 
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import uuid

app = Flask(__name__)

JSON_FILE = "students.json"
WORKSHOP_JSON = "workshop.json"
CONFERENCE_PART_JSON="confernceparticipant.json"
OUTPUT_FOLDER = "generated"
TEMPLATE = "templates/template.jpg"
CERT_FOLDER = "certificates"
ZIP_FILE = "certificates.zip"
WORKSHOP_ZIP = "workshop_certificates.zip"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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

# download certificates of conference presentation

@app.route("/download-all-certificates")
def download_all_certificates():

    if not os.path.exists(JSON_FILE):
        return "No student data found."

    with open(JSON_FILE, "r") as f:
        students = json.load(f)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for student in students:
            name = student["name"]
            college = student["college"]
            paper = student["paper_title"]

            safe_name = name.replace(" ", "_")

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
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
<b>{paper}</b> in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR SUSTAINABLE
FUTURE"</b> organised by <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> from <b>05/02/2026 to 06/02/2026</b>.
"""

            frame = Frame(87, 180, width - 180, 210, showBoundary=0)
            frame.addFromList([Paragraph(text, style)], c)

            c.save()
            pdf_buffer.seek(0)
            zipf.writestr(f"{safe_name}.pdf", pdf_buffer.read())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="all_certificates.zip",
        mimetype="application/zip"
    )

#conference certficatinte all certifcate downloaded page

@app.route('/conferencealldownload')
def conferencealldownload():
    return render_template("conferencealldownload.html")

#dynamic certificate template generating software

# @app.route("/generate-dynamic-certificates", methods=["POST"])
# def generate_dynamic_certificates():

#     if not os.path.exists(JSON_FILE):
#         return "No student data found."

#     cert_type = request.form.get("cert_type")
#     program_name = request.form.get("program_name")
#     organized_by = request.form.get("organized_by")
#     event_date = request.form.get("event_date")

#     coordinators = request.form.getlist("coordinators[]")
#     coordinators = [c for c in coordinators if c.strip()]

#     with open(JSON_FILE, "r") as f:
#         students = json.load(f)

#     zip_name = "dynamic_certificates.zip"

#     with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:

#         for student in students:
#             name = student["name"]
#             college = student["college"]
#             paper = student.get("paper_title", "")

#             safe_name = name.replace(" ", "_")
#             pdf_path = os.path.join(CERT_FOLDER, f"{safe_name}.pdf")

#             c = canvas.Canvas(pdf_path, pagesize=A4)
#             width, height = A4

#             c.drawImage("template.jpg", 0, 0, width, height)

#             c.setFont("CasusPro-Bold", 18)
#             c.drawCentredString(width / 2, 470, "PRESENTATION CERTIFICATE")

#             c.setFont("CasusPro", 12)
#             c.drawCentredString(width / 2, 445, "This is to certify that")

#             c.setFont("CasusPro-Bold", 20)
#             c.drawCentredString(width / 2, 415, name)

#             style = ParagraphStyle(
#                 name="CertBody",
#                 fontName="CasusPro",
#                 fontSize=12,
#                 leading=18,
#                 alignment=TA_JUSTIFY
#             )

#             if cert_type == "best_paper":
#                 body_text = f"""
# of <b>{college}</b> has presented a paper titled as
# <b>{paper}</b> and it is selected as the Best Paper in the
# <b>{program_name}</b> organised by
# <b>{organized_by}</b>
# From <b>{event_date}</b>.
# """
#             elif cert_type == "presentation":
#                 body_text = f"""
# of <b>{college}</b> has presented a paper titled as
# <b>{paper}</b> in the
# <b>{program_name}</b> organised by
# <b>{organized_by}</b>
# From <b>{event_date}</b>.
# """
#             else:
#                 body_text = f"""
# of <b>{college}</b> has actively participated in the
# <b>{program_name}</b> organised by
# <b>{organized_by}</b>
# On <b>{event_date}</b>.
# """

#             frame = Frame(85, 200, width - 170, 180, showBoundary=0)
#             frame.addFromList([Paragraph(body_text, style)], c)
#             c.setFont("CasusPro", 9)

#             if len(coordinators) == 2:
#                 x_positions = [200, 400]
#             elif len(coordinators) == 3:
#                 x_positions = [140, 300, 460]
#             else:
#                 x_positions = []

#             for i, coord in enumerate(coordinators):
#                 c.drawCentredString(x_positions[i], 115, coord)
#                 c.drawCentredString(x_positions[i], 100, "Coordinator")

#             c.save()
#             zipf.write(pdf_path, arcname=f"{safe_name}.pdf")

#     return send_file(zip_name, as_attachment=True)


@app.route("/dynamic_event_cert")
def dynamic_event_cert():
    signatures = [
        f for f in os.listdir("signatures")
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    return render_template(
        "Eventcertificatepage.html",
        signatures=signatures
    )

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
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for student in students:
            name = student["name"]
            college = student["college"]
            paper = student["paper_title"]
            safe_name = name.replace(" ", "_")
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
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
 <b>{college}</b> has participated in the
<b>INTERNATIONAL CONFERENCE ON "VIKSIT BHARAT 2047:
INTEGRATING BUSINESS, TECHNOLOGY AND
COMPUTATIONAL MATHEMATICS FOR A SUSTAINABLE
FUTURE"</b>, organised by the <b>DEPARTMENT OF COMPUTER
APPLICATIONS</b> from <b>05/02/2026 to 06/02/2026</b>.
"""

            frame = Frame(87, 180, width - 180, 210, showBoundary=0)
            frame.addFromList([Paragraph(text, style)], c)
            c.save()
            pdf_buffer.seek(0)
            zipf.writestr(f"{safe_name}.pdf", pdf_buffer.read())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="all_conference_participation_certificates.zip"
    )


#dynamically creating event 

@app.route("/create-event", methods=["POST"])
def create_event():

    program_name = request.form.get("program_name")
    safe_event = program_name.replace(" ", "_")

    event_data = {
        "cert_type": request.form.get("cert_type"),
        "program_name": program_name,
        "organized_by": request.form.get("organized_by"),
        "event_date": request.form.get("event_date"),
        "coordinators": []
    }

    for i in range(1, 4):
        desig = request.form.get(f"coord_desig_{i}")
        name = request.form.get(f"coord_name_{i}")
        sign = request.form.get(f"coord_sign_{i}")

        if desig and name and sign:
            event_data["coordinators"].append({
                "designation": desig,
                "name": name,
                "signature": f"signatures/{sign}"
            })

    event_meta_path = f"events/event_meta/{safe_event}.json"
    with open(event_meta_path, "w") as f:
        json.dump(event_data, f, indent=4)
    student_file = f"events/event_students/{safe_event}_students.json"
    with open(student_file, "w") as f:
        json.dump([], f, indent=4)

    return redirect("/events")

#dynamic event gneration view and add students and download certficate

@app.route("/events")
def events():
    files = os.listdir("events/event_meta")
    events = [f.replace(".json", "").replace("_", " ") for f in files]
    return render_template("events.html", events=events)


@app.route("/add-student")
def add_student():
    files = os.listdir("events/event_students")

    events = []
    for f in files:
        if f.endswith("_students.json"):
            events.append({
                "display": f.replace("_students.json", "").replace("_", " "),
                "file": f
            })

    return render_template("eventsinsertform.html", events=events)

@app.route("/save-student", methods=["POST"])
def save_student():
    event_file = request.form.get("event_file")
    path = f"events/event_students/{event_file}"

    new_student = {
        "name": request.form.get("name"),
        "college": request.form.get("college")
    }

    with open(path, "r") as f:
        students = json.load(f)

    students.append(new_student)

    with open(path, "w") as f:
        json.dump(students, f, indent=4)

    return redirect("/events")

@app.route("/view-event/<event_name>")
def view_event(event_name):
    file_name = f"{event_name}_students.json"
    path = f"events/event_students/{file_name}"

    if not os.path.exists(path):
        return "No data found"

    with open(path, "r") as f:
        data = json.load(f)

    readable_name = event_name.replace("_", " ")

    return render_template(
        "view_event.html",
        data=data,
        event_name=readable_name,
        event_file=file_name
    )

@app.route("/delete-student/<event_file>/<int:index>")
def delete_student(event_file, index):
    path = f"events/event_students/{event_file}"

    with open(path, "r") as f:
        students = json.load(f)

    if 0 <= index < len(students):
        students.pop(index)

    with open(path, "w") as f:
        json.dump(students, f, indent=4)

    event_name = event_file.replace("_students.json", "")
    return redirect(f"/view-event/{event_name}")

@app.route("/download-certificates/<event_name>")
def download_certificates(event_name):

    meta_path = f"events/event_meta/{event_name}.json"
    students_path = f"events/event_students/{event_name}_students.json"

    if not os.path.exists(meta_path) or not os.path.exists(students_path):
        return "Event data not found", 404

    with open(meta_path, "r") as f:
        event = json.load(f)

    with open(students_path, "r") as f:
        students = json.load(f)

    if not students:
        return "No students available", 400

    os.makedirs("generated", exist_ok=True)
    os.makedirs("certificates", exist_ok=True)

    zip_path = f"certificates/{event_name}_certificates.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:

        for student in students:
            safe_name = student["name"].replace(" ", "_")
            pdf_path = f"generated/{safe_name}.pdf"

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            c.drawImage("template.jpg", 0, 0, width, height)

            cert_type = event.get("certificate_type", "PARTICIPATION CERTIFICATE")

            c.setFont("CasusPro-Bold", 17)
            c.drawCentredString(width / 2, 485, cert_type)

            c.setFont("CasusPro-Bold", 16)
            c.drawCentredString(width / 2, 409, student["name"])

            style = ParagraphStyle(
                name="CertText",
                fontName="CasusPro",
                fontSize=16,
                leading=24,
                alignment=TA_JUSTIFY
            )

            paragraph_text = f"""
            of <b>{student['college']}</b> has successfully participated in
            <b>{event['program_name']}</b> organised by
            <b>{event['organized_by']}</b> on
            <b>{event['event_date']}</b>.
            """

            frame = Frame(
                x1=90,
                y1=190,
                width=width - 180,
                height=190,
                showBoundary=0
            )

            frame.addFromList([Paragraph(paragraph_text, style)], c)
            sig_y = 90
            start_x = 60
            gap = (width - 100) / len(event["coordinators"])

            for i, coord in enumerate(event["coordinators"]):
                x = start_x + i * gap  
                if os.path.exists(coord["signature"]):
                    c.drawImage(
                        coord["signature"],
                        x,
                        sig_y + 60,
                        width=120,
                        height=45,
                        mask="auto"
                    )

                c.setFont("CasusPro-Bold", 12)
                c.drawCentredString(x + 50, sig_y + 20, coord["designation"])
                c.setFont("CasusPro-Bold", 12)
                c.drawCentredString(x + 53, sig_y+5, f"({coord['name']})")

            c.save()

            zipf.write(pdf_path, f"{safe_name}.pdf")
            os.remove(pdf_path)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
