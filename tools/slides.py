from pypdf import PdfReader
import os


def save_uploaded_file(file_bytes, filename):
    os.makedirs("uploads", exist_ok=True)

    path = os.path.join("uploads", filename)

    with open(path, "wb") as f:
        f.write(file_bytes)

    return path


def parse_pdf(path):
    reader = PdfReader(path)

    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()

        if text:
            pages.append({
                "page": i + 1,
                "text": text
            })

    return pages


def slide_context(pages):
    combined = []

    for page in pages:
        combined.append(f"Slide {page['page']}:\n{page['text']}")

    return "\n\n".join(combined)