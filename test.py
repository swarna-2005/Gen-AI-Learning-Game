import fitz  # PyMuPDF for reading PDFs
import google.generativeai as genai

# Configure API key
API_KEY = "AIzaSyA029gTN0ennJyu_pZjefLF_IwBmFsgbJM"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

# Load the Generative Model
model = genai.GenerativeModel('gemini-1.5-flash-8b-exp-0924')

def extract_text_from_pdf(pdf_path, max_pages=5):
    """Extract text from a PDF file (limited to `max_pages` pages)."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(min(max_pages, len(doc))):
        text += doc[page_num].get_text("text") + "\n"
    return text

def summarize_text(text):
    """Summarize text using Gemini AI."""
    response = model.generate_content(f"Summarize the following text concisely:\n{text}")
    return response.text if response else "Error in summarization."

def generate_comical_story(summary):
    """Generate a short comical story based on the summary."""
    response = model.generate_content(f"Create a funny short story based on this summary:\n{summary}")
    return response.text if response else "Error in generating story."

# Example usage
pdf_file = "C:\\Users\\ciran\\Downloads\\CertificateOfCompletion_Python Data Analysis 2020 (1).pdf"
  # Replace with your PDF file path
pdf_text = extract_text_from_pdf(pdf_file)
summary = summarize_text(pdf_text)
comical_story = generate_comical_story(summary)

print("\n**Summary:**\n", summary)
print("\n**Comical Story:**\n", comical_story)
