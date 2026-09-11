from PyPDF2 import PdfReader
from flask import Flask, render_template, request, redirect
import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

report_text = ""
report_result = ""
report_summary = ""
chat_history = []

client = genai.Client(api_key=os.getenv('GENAI_API_KEY'))

app = Flask(__name__)
report_text = ""

UPLOAD_FOLDER = "upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def landing():
    return render_template("LandingPage.html")

@app.route("/home")
def home():
    return render_template("index.html", message="No Report Upload Yet")


@app.route("/upload", methods=["POST"])
def upload_file():
    global report_text
    file = request.files["report"]
     
    if file.filename == "":
        return render_template("index.html", message="No File Selected")

    # File Save
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)

    file.save(file_path)

    try:

        # PDF Read
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
        # Terminal me pura text print hogac
        print(text)
        report_text = text

        # Gemini se connection
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
            You are an expert AI Health Report Analyzer.

            Analyze the following medical report carefully.

            Rules:
            - Use only the information available in the report.
            - Do NOT guess or invent values.
            - If any information is missing, clearly mention "Not Available".
            - Explain in simple language that a non-medical person can understand.

            Return your answer in exactly this format:

            🩺 Overall Health Summary
              (2-4 lines)

            📊 Abnormal Parameters
            - Parameter Name
            - Current Value
            - Normal Range (if available)
            - Why it matters
   
        🟢 Normal Parameters
        (List important normal findings)

        🥗 Lifestyle & Diet Suggestions
        (Practical diet and lifestyle tips)

        ⚠️ Important Note
        (This analysis is for informational purposes only and is not a medical diagnosis. Consult a qualified healthcare professional for medical advice.)
 
       Medical Report:
       {text[:3000]}
        """
         )

        print(response.text)
        ai_summary = response.text

        hba1c = re.search(
            r"(HbA1c|Hb A1C|HBA1C|Hemoglobin A1c|Hemoglobin A1C|Glycated Hemoglobin|Glycosylated Hemoglobin|A1C).*?(\d+\.?\d*)",
            text,
            re.IGNORECASE,
        )

        blood_glucose = re.search(
            r"(Blood Glucose|Blood Sugar|Glucose|FBS|Fasting Blood Sugar|Fasting Plasma Glucose|FPG|Glucose Fasting).*?(\d+\.?\d*)",
            text,
            re.IGNORECASE,
        )

        cholesterol = re.search(
            r"(Total Cholesterol|Cholesterol|Serum Cholesterol|Cholesterol Total).*?(\d+\.?\d*)",
            text,
            re.IGNORECASE,
        )

        vitamin_d = re.search(
            r"(Vitamin D|Vitamin D3|25-OH Vitamin D|25 Hydroxy Vitamin D|25-Hydroxy Vitamin D).*?(\d+\.?\d*)",
            text,
            re.IGNORECASE,
        )

        hdl = re.search(
            r"(HDL|HDL Cholesterol|High Density Lipoprotein).*?(\d+\.?\d*)",
            text,
            re.IGNORECASE,
        )

        ldl = re.search(
            r"(LDL|LDL Cholesterol|Low Density Lipoprotein).*?(\d+\.?\d*)",
            text,
            re.IGNORECASE,
        )

        triglycerides = re.search(
            r"(Triglycerides|Triglyceride|TG).*?(\d+\.?\d*)", text, re.IGNORECASE
        )

        result = ""

        # ---------------- HbA1c ----------------

        if hba1c:

            value = float(hba1c.group(2))

            if value < 5.7:
                status = "🟢 Normal"

            elif value < 6.5:
                status = "🟡 Prediabetes"

            else:
                status = "🔴 Diabetes Risk"

            result += f"✅ HbA1c : {value}%\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ HbA1c Not Found\n\n"

            # ---------------- Blood Glucose ----------------

        if blood_glucose:

            value = float(blood_glucose.group(2))

            if value < 100:
                status = "🟢 Normal"

            elif value < 126:
                status = "🟡 Prediabetes"

            else:
                status = "🔴 Diabetes Risk"

            result += f"✅ Blood Glucose : {value} mg/dL\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ Blood Glucose Not Found\n\n"

            # ---------------- Cholesterol ----------------

        if cholesterol:

            value = float(cholesterol.group(2))

            if value < 200:
                status = "🟢 Normal"

            elif value < 240:
                status = "🟡 Borderline High"

            else:
                status = "🔴 High"

            result += f"✅ Cholesterol : {value} mg/dL\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ Cholesterol Not Found\n\n"

            # ---------------- HDL ----------------

        if hdl:

            value = float(hdl.group(2))

            if value >= 60:
                status = "🟢 Good"

            elif value >= 40:
                status = "🟡 Acceptable"

            else:
                status = "🔴 Low"

            result += f"✅ HDL : {value} mg/dL\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ HDL Not Found\n\n"

            # ---------------- LDL ----------------

        if ldl:

            value = float(ldl.group(2))

            if value < 100:
                status = "🟢 Optimal"

            elif value < 130:
                status = "🟡 Near Optimal"

            elif value < 160:
                status = "🟠 Borderline High"

            else:
                status = "🔴 High"

            result += f"✅ LDL : {value} mg/dL\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ LDL Not Found\n\n"

            # ---------------- Triglycerides ----------------

        if triglycerides:

            value = float(triglycerides.group(2))

            if value < 150:
                status = "🟢 Normal"

            elif value < 200:
                status = "🟡 Borderline High"

            elif value < 500:
                status = "🟠 High"

            else:
                status = "🔴 Very High"

            result += f"✅ Triglycerides : {value} mg/dL\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ Triglycerides Not Found\n\n"

            # ---------------- Vitamin D ----------------

        if vitamin_d:

            value = float(vitamin_d.group(2))

            if value < 20:
                status = "🔴 Deficient"

            elif value < 30:
                status = "🟡 Insufficient"

            elif value <= 100:
                status = "🟢 Normal"

            else:
                status = "🟠 High"

            result += f"✅ Vitamin D : {value} ng/mL\n"
            result += f"Status : {status}\n\n"

        else:
            result += "❌ Vitamin D Not Found\n\n"

        global report_result, report_summary

        report_result = result
        report_summary = ai_summary

        return render_template(
            "index.html",
            message=report_result,
            ai_summary=report_summary,
        )

    except Exception as e:
        return render_template("index.html", message=f"Error reading PDF: {str(e)}")


@app.route("/ask", methods=["POST"])
def ask_ai():

    global report_text, report_result, report_summary, chat_history

    question = request.form["question"]
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            You are an AI Health Report Analyzer Agent.

            This is the patient's health report:

            {report_text}

            Answer ONLY based on this report.

            User Question:
            {question}
        """,
        )

        ai_answer = response.text

    except Exception as e:
     print(e)
     ai_answer = f"⚠️ {e}"

    chat_history.append({
    "role": "user",
    "message": question
     })

    chat_history.append({
    "role": "ai",
    "message": ai_answer
     })
    return render_template(
        "index.html",
        message=report_result,
        ai_summary=report_summary,
        ai_answer=ai_answer,
        chat_history=chat_history,
    )

if __name__ == "__main__":
    app.run(debug=True)
