import os
from typing import List

def get_all_pdf_files(directory: str) -> List[str]:
    """
    Get all PDF files from the specified directory.
    """
    pdf_files = []
    if os.path.exists(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    return pdf_files
