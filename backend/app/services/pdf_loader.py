from pathlib import Path
from typing import List
from pypdf import PdfReader


class PDFLoader:
    """
    Handles reading PDF files and extracting text.
    """

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from a single PDF.
        """

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    def load_documents(self, folder_path: str) -> List[dict]:
        """
        Load every PDF inside the folder.
        """

        documents = []

        pdf_files = Path(folder_path).glob("*.pdf")
        
        for pdf in pdf_files:

            reader = PdfReader(str(pdf))

            for page_number, page in enumerate(reader.pages, start=1):

                text = page.extract_text()

                if text:
                    documents.append({
                    "filename": pdf.name,
                    "page": page_number,
                    "text": text
                })
        return documents