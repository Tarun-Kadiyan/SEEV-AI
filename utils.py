import io, csv
from pypdf import PdfReader
from docx import Document

def extract_text(data, filename):
    name = (filename or "").lower()
    try:
        if name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if name.endswith(".docx"):
            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def make_report(filename, score, result):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Resume", "Match score", "Recommendation", "Matched skills", "Missing skills"])
    writer.writerow([filename, score, result["recommendation"],
                     ", ".join(result["matched_skills"]), ", ".join(result["missing_skills"])])
    return output.getvalue().encode("utf-8")
