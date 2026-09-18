from PyPDF2 import PdfReader
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

# App Setup and Secret Key for Session
app = Flask(__name__)
app.secret_key = "my_super_secret_key"  #[cite: 1]

# ==========================================
# 1. DATABASE CONFIGURATION[cite: 1]
# ==========================================
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Table Schema[cite: 1]
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# ==========================================
# 2. FILE UPLOAD & HYBRID AI CONFIGURATION[cite: 1]
# ==========================================
UPLOAD_FOLDER = "upload"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = genai.Client(api_key=os.getenv('GENAI_API_KEY'))

# Global Variables[cite: 1]
report_text = ""
report_result = ""
report_summary = ""
chat_history = []


def get_ai_response(prompt_text):
    """
    Hybrid AI Fallback: Tries Gemini Cloud first, 
    if it fails or network drops, switches to local Ollama 3b.
    """
    try:
        # 1. Try Gemini Cloud API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text
        )
        return response.text
        
    except Exception as e:
        print(f"⚠️ Gemini Cloud Failed ({e}). Switching to Local Ollama 3b...")
        
        try:
            # 2. Fallback to Local Ollama (Port 11434)
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": "qwen2.5:3b",  # 👈 YAHAN SIRF MODEL KA NAAM CHANGE KIYA HAI
                "prompt": prompt_text,
                "stream": False
            }
            
           # Send POST request to Local Ollama
            res = requests.post(ollama_url, json=payload, timeout=180)
            if res.status_code == 200:
                return res.json().get("response", "No response from local Ollama.")
            else:
                return f"❌ Error: Local Ollama responded with status {res.status_code}"
                
        except Exception as ollama_err:
            return f"❌ Critical Error: Both Cloud AI and Local Ollama are offline. Details: {ollama_err}"


# ==========================================
# 3. ROUTES[cite: 1]
# ==========================================

@app.route("/")
def landing():
    if 'user_id' in session:
        return redirect("/home")
    return render_template("LandingPage.html")

# --- AUTHENTICATION ROUTES ---[cite: 1]

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered. Please Login."
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect("/login")
        
    return render_template("AuthPage.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect("/home")
        else:
            return "Invalid Email or Password. Try Again."
            
    return render_template("AuthPage.html", mode="login")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect("/")

# --- MAIN APP ROUTES ---[cite: 1]

@app.route("/home")
def home():
    if 'user_id' not in session:
        return redirect("/login")
    return render_template("index.html", message="No Report Upload Yet", user_name=session.get('user_name'))

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'user_id' not in session:
        return redirect("/login")
        
    global report_text
    file = request.files["report"]
     
    if file.filename == "":
        return render_template("index.html", message="No File Selected", user_name=session.get('user_name'))

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        report_text = text

        prompt_content = f"""
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

        # Using Hybrid Fallback Function
        ai_summary = get_ai_response(prompt_content)

        # RegEx Parsing logic (Matched from your original code)[cite: 1]
        # RegEx Parsing logic (Updated for Newlines in PDF)
        hba1c = re.search(r"(HbA1c|Hb A1C|HBA1C|Hemoglobin A1c|Glycated Hemoglobin|A1C)[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)
        blood_glucose = re.search(r"(Blood Glucose|Blood Sugar|Glucose|FBS|Fasting Blood Sugar|FPG)[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)
        cholesterol = re.search(r"(Total Cholesterol|Cholesterol|Serum Cholesterol)[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)
        
        # Vitamin D mein '(25-OH)' add kiya hai taaki wo usko value na samajh le
        vitamin_d = re.search(r"(Vitamin D|Vitamin D3|25-OH Vitamin D|Vitamin D \(25-OH\))[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)
        
        hdl = re.search(r"(HDL|HDL Cholesterol)[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)
        ldl = re.search(r"(LDL|LDL Cholesterol)[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)
        triglycerides = re.search(r"(Triglycerides|Triglyceride|TG)[\s\S]{1,20}?(\d+\.?\d*)", text, re.IGNORECASE)

        result = ""

        if hba1c:
            value = float(hba1c.group(2))
            if value < 5.7: status = "🟢 Normal"
            elif value < 6.5: status = "🟡 Prediabetes"
            else: status = "🔴 Diabetes Risk"
            result += f"✅ HbA1c : {value}%\nStatus : {status}\n\n"
        else:
            result += "❌ HbA1c Not Found\n\n"

        if blood_glucose:
            value = float(blood_glucose.group(2))
            if value < 100: status = "🟢 Normal"
            elif value < 126: status = "🟡 Prediabetes"
            else: status = "🔴 Diabetes Risk"
            result += f"✅ Blood Glucose : {value} mg/dL\nStatus : {status}\n\n"
        else:
            result += "❌ Blood Glucose Not Found\n\n"

        if cholesterol:
            value = float(cholesterol.group(2))
            if value < 200: status = "🟢 Normal"
            elif value < 240: status = "🟡 Borderline High"
            else: status = "🔴 High"
            result += f"✅ Cholesterol : {value} mg/dL\nStatus : {status}\n\n"
        else:
            result += "❌ Cholesterol Not Found\n\n"

        if hdl:
            value = float(hdl.group(2))
            if value >= 60: status = "🟢 Good"
            elif value >= 40: status = "🟡 Acceptable"
            else: status = "🔴 Low"
            result += f"✅ HDL : {value} mg/dL\nStatus : {status}\n\n"
        else:
            result += "❌ HDL Not Found\n\n"

        if ldl:
            value = float(ldl.group(2))
            if value < 100: status = "🟢 Optimal"
            elif value < 130: status = "🟡 Near Optimal"
            elif value < 160: status = "🟠 Borderline High"
            else: status = "🔴 High"
            result += f"✅ LDL : {value} mg/dL\nStatus : {status}\n\n"
        else:
            result += "❌ LDL Not Found\n\n"

        if triglycerides:
            value = float(triglycerides.group(2))
            if value < 150: status = "🟢 Normal"
            elif value < 200: status = "🟡 Borderline High"
            elif value < 500: status = "🟠 High"
            else: status = "🔴 Very High"
            result += f"✅ Triglycerides : {value} mg/dL\nStatus : {status}\n\n"
        else:
            result += "❌ Triglycerides Not Found\n\n"

        if vitamin_d:
            value = float(vitamin_d.group(2))
            if value < 20: status = "🔴 Deficient"
            elif value < 30: status = "🟡 Insufficient"
            elif value <= 100: status = "🟢 Normal"
            else: status = "🟠 High"
            result += f"✅ Vitamin D : {value} ng/mL\nStatus : {status}\n\n"
        else:
            result += "❌ Vitamin D Not Found\n\n"

        global report_result, report_summary
        report_result = result
        report_summary = ai_summary

        return render_template(
            "index.html",
            message=report_result,
            ai_summary=report_summary,
            user_name=session.get('user_name')
        )

    except Exception as e:
        return render_template("index.html", message=f"Error reading PDF: {str(e)}", user_name=session.get('user_name'))

@app.route("/ask", methods=["POST"])
def ask_ai():
    if 'user_id' not in session:
        return redirect("/login")
        
    global report_text, report_result, report_summary, chat_health_history, chat_history
    question = request.form["question"]
    
    prompt_content = f"""
    You are an AI Health Report Analyzer Agent.
    This is the patient's health report:
    {report_text}
    Answer ONLY based on this report.
    User Question:
    {question}
    """
    
    ai_answer = get_ai_response(prompt_content)

    chat_history.append({"role": "user", "message": question})
    chat_history.append({"role": "ai", "message": ai_answer})
    
    return render_template(
        "index.html",
        message=report_result,
        ai_summary=report_summary,
        ai_answer=ai_answer,
        chat_history=chat_history,
        user_name=session.get('user_name')
    )

if __name__ == "__main__":
    app.run(debug=True)