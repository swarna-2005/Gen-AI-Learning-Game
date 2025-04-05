from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import sqlite3
import os

# Configure Gemini API
API_KEY = "AIzaSyA029gTN0ennJyu_pZjefLF_IwBmFsgbJM"  # Replace with your API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b-exp-0924')

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS

# Database settings
DB_NAME = "quiz.db"

def create_table():
    """Ensures the quiz table exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()  # Ensure table is created at startup

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_quiz', methods=['POST','GET'])
def generate_quiz():
    """Generates and stores a quiz in the database."""
    try:
        data = request.json
        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Generate quiz using Gemini AI
        prompt = f"""
        Generate 10 multiple-choice questions on '{topic}' with exactly 4 options each.
        Format each question exactly like this:
        Q: [Your question here]
        A: [Option A]
        B: [Option B]
        C: [Option C]
        D: [Option D]
        Answer: [Correct option letter A/B/C/D]
        
        Ensure each question follows this format precisely with no additional text.
        """

        response = model.generate_content(prompt)

        if not response.text:
            return jsonify({"error": "Failed to get response from AI"}), 500

        raw_text = response.text
        questions = []
        parts = [p for p in raw_text.strip().split("\n\n") if p.strip()]  # Split by double newlines

        for part in parts:
            lines = [line.strip() for line in part.split("\n") if line.strip()]
            if len(lines) >= 6:
                try:
                    question = lines[0].replace("Q:", "").strip()
                    options = {}
                    for line in lines[1:5]:
                        if ":" in line:
                            opt, val = line.split(":", 1)
                            options[opt.strip().upper()] = val.strip()
                    
                    correct_answer = lines[5].split(":")[-1].strip().upper() if "Answer:" in lines[5] else ""

                    questions.append({
                        "topic": topic,
                        "question": question,
                        "option_a": options.get("A", ""),
                        "option_b": options.get("B", ""),
                        "option_c": options.get("C", ""),
                        "option_d": options.get("D", ""),
                        "correct_answer": correct_answer
                    })
                except Exception as e:
                    print(f"Error parsing question: {e}")
                    continue

        # Clear previous questions on the same topic
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz WHERE topic = ?", (topic,))
        
        # Store new quiz in database
        for quiz in questions:
            cursor.execute(
                "INSERT INTO quiz (topic, question, option_a, option_b, option_c, option_d, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (quiz["topic"], quiz["question"], quiz["option_a"], quiz["option_b"], 
                 quiz["option_c"], quiz["option_d"], quiz["correct_answer"]))
        conn.commit()
        conn.close()

        return jsonify({"message": "Quiz generated successfully!", "quiz": questions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_quiz', methods=['GET'])
def get_quiz():
    """Retrieves the generated quiz from the database."""
    try:
        topic = request.args.get('topic', '').strip()
        if not topic:
            return jsonify({"error": "Topic parameter is required"}), 400

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz WHERE topic = ?", (topic,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return jsonify({"error": "No quiz found for this topic"}), 404

        quiz = []
        for row in rows:
            quiz.append({
                "id": row[0],
                "topic": row[1],
                "question": row[2],
                "option_a": row[3],
                "option_b": row[4],
                "option_c": row[5],
                "option_d": row[6],
                "correct_answer": row[7]
            })

        return jsonify({"quiz": quiz}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)
@app.route('/test-static')
def test_static():
    test_files = {
        'CSS': url_for('static', filename='css/style.css'),
        'Favicon': url_for('static', filename='images/favicon.ico'),
        'Logo': url_for('static', filename='images/logo.png'),
        'Trophy Icon': url_for('static', filename='images/icons/trophy.svg'),
        'Quiz Icon': url_for('static', filename='images/icons/quiz.svg')
    }
    
    html = "<h1>Static Files Test</h1><ul>"
    for name, path in test_files.items():
        status = "✅" if os.path.exists(path[1:]) else "❌"
        html += f'<li>{status} {name}: <a href="{path}">{path}</a></li>'
    html += "</ul>"
    
    return html


import fitz  # PyMuPDF for PDF parsing
from flask import request, jsonify
import google.generativeai as genai
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    return text.strip()

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """Handles PDF upload, extracts content, and summarizes it."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Invalid file format. Please upload a PDF."}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    pdf_text = extract_text_from_pdf(file_path)

    prompt = f"Summarize the following content in 200 words:\n\n{pdf_text[:2000]}"
    response = model.generate_content(prompt)
    summary = response.text if response.text else "Summary generation failed."

    story_prompt = f"Write a short humorous story inspired by this summary:\n\n{summary}"
    story_response = model.generate_content(story_prompt)
    story = story_response.text if story_response.text else "Story generation failed."

    return jsonify({"summary": summary, "story": story}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)