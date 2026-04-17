from django.shortcuts import render
from app.modules import main as mp
import os
from django.http import JsonResponse
from django.conf import settings
from .models import DamageReport
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings
# Create your views here.
import json
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.templatetags.static import static
from google import genai
import json

global location, distance

def upload_image(request):
    global location, distance
    if request.method == "POST":
        image = request.FILES.get("image")

        if not image:
            return JsonResponse({"status": "error", "message": "No file"})

        upload_dir = os.path.join(settings.BASE_DIR, "app/static/uploads")

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # 🔥 FIXED NAME (always same)
        file_path = os.path.join(upload_dir, "image.jpg")

        # 🔥 DELETE OLD FILE IF EXISTS
        if os.path.exists(file_path):
            os.remove(file_path)

        # 🔥 SAVE NEW FILE
        with open(file_path, "wb+") as f:
            for chunk in image.chunks():
                f.write(chunk)

        print("Saved (replaced):", file_path)

        location = request.POST.get("location")
        distance = request.POST.get("distance")
        request.session["location"] = location
        request.session["distance"] = distance

        print("Location:", location)
        print("Distance:", distance)

        return JsonResponse({
            "status": "success",
            "path": "static/uploads/image.jpg"
        })

def home(request):

    return render(request, 'app/index.html')

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    return render(request, 'app/contact.html')

def pubilc(request):
    value = mp.getdata()   # this returns JSON string
    value2=mp.getdata()
    data = json.loads(value)   # convert JSON string → dict
    data2 = json.loads(value2)
    return render(request, 'app/pubilc.html', {"data": data,"data2":data2})


def report2(request):
    value=mp.getdata()
    value2=mp.getdata()
    data = json.loads(value)   # convert JSON string → dict
    data2 = json.loads(value2)
    return render(request, 'app/report2.html', {"data": data,"data2":data2})

def public3(request):
    return render(request, 'app/public3.html')

def index(request):
    return render(request, 'app/index.html')

def myreports(request):
    return render(request, 'app/myreports.html')
def view_pdf(request, id):
    file_path = os.path.join(
        settings.BASE_DIR,
        f"app/static/reports/report_{id}.pdf"
    )

    if not os.path.exists(file_path):
        raise Http404("PDF not found")

    return FileResponse(open(file_path, "rb"), content_type="application/pdf")


def officer(request):

    reports = DamageReport.objects.all()

    # 🔥 COUNTS
    critical_count = 0
    pending_count = reports.filter(status="pending").count()
    approved_count = reports.filter(status="approved").count()
    resolved_count = reports.filter(status="resolved").count()

    # 🔥 count critical from JSON
    for r in reports:
        if r.data.get("damage", {}).get("level") == "critical":
            critical_count += 1

    context = {
        "critical": critical_count,
        "pending": pending_count,
        "active": approved_count,
        "resolved": resolved_count
    }

    return render(request, 'app/officer.html', context)

def role(request):
    return render(request, 'app/role.html')

def login(request):
    return render(request, 'app/login.html')



def report(request):
    location = request.session.get("location", "unknown")

    value = mp.getdata()
    data = json.loads(value)

    

    # Set your API key here
    api_key = "AIzaSyXXXXXXXXXXXX"

    # Initialize the client once
    client = genai.Client(api_key=api_key)
    Result=data["results"][0]
    full_prompt = f"""
You are a civil engineering expert specializing in infrastructure damage assessment and repair.

Analyze the given infrastructure damage and provide a short simple response.

Your response must include only plain text with no special characters no bullets no symbols no markdown.

Follow this structure exactly in simple sentences

Risk Assessment
Explain safety risk in simple words
Give severity level as Low Medium High or Critical
Explain possible consequences if not repaired

Repair Procedure
Explain how to fix the damage step by step in simple sentences
List required materials and tools in a sentence
Give simple preventive measures to avoid future damage

Damage details are {Result}

Return a clear short AI suggestion for officials to understand quickly
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)
    raw = response.text.strip()

    print(raw)

    result = data["results"][0]
    result["location"]["area"] = location

    # ✅ SAVE TO DB
    report_obj = DamageReport.objects.create(
        data=result,
        damage_type=result["damage"]["type"],
        location=location
    )
    overlay_url = request.build_absolute_uri(
    static("processimage/overlay.jpg")
    )


    # ✅ GENERATE PDF (AUTO)
    template = get_template("app/report_pdf.html")  # ⚠️ NOT report.html
    html = template.render({
        "data": result,
        "report_id": report_obj.id,
        "overlay_url":overlay_url
    })

    pdf_dir = os.path.join(settings.BASE_DIR, "app/static/reports")
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    pdf_file = f"report_{report_obj.id}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_file)

    with open(pdf_path, "wb") as f:
        pisa.CreatePDF(html, dest=f)

    # ✅ SAVE PATH
    report_obj.pdf = f"static/reports/{pdf_file}"
    report_obj.save()

    print("Saved Report ID:", report_obj.id)
    print("PDF Saved:", report_obj.pdf)

    return render(request, 'app/report.html', {
        "data": result,
        "report_id": report_obj.id,
        "ai_sujjection": raw
    })


def get_location_name(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
        res = requests.get(url, headers={"User-Agent": "crackeye-app"})
        data = res.json()

        return data.get("display_name", "Unknown Location")

    except:
        return "Unknown Location"
    
def get_reports(request):
    reports = DamageReport.objects.all().order_by('-created_at')

    data = []

    for r in reports:
        d = r.data

        area = d["location"].get("area", "")

        lat, lng = None, None
        location_name = "Unknown"

        # ✅ Convert "lat, lng" string → float
        if area and "," in area:
            try:
                lat_str, lng_str = area.split(",")
                lat = float(lat_str.strip())
                lng = float(lng_str.strip())

                # ✅ Get readable location
                location_name = get_location_name(lat, lng)

            except:
                location_name = area  # fallback

        data.append({
            "id": r.id,
            "location": location_name,   # 🔥 human readable
            "severity": d["damage"]["level"],
            "status": "pending",
            "lat": lat,
            "lng": lng,
            "timestamp": r.created_at.strftime("%H:%M"),
            "description": f'{d["damage"]["type"]} detected with {d["damage"]["level"]} severity'
        })

    return JsonResponse({"cases": data})



