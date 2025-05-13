import pdfplumber
import os

# Define the PDF path
pdf_path = "G:/My Drive/Deftech/SmartSteps/smart_steps_ai/personas/Jane/Jane-Early Trauma and Giftedness in Context.pdf"
txt_path = "G:/My Drive/Deftech/SmartSteps/smart_steps_ai/personas/Jane/Jane-Early.txt"

try:
    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        # Get the text from each page
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n\n"
        
        # Write the text to a file
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
        
        print(f"Successfully converted {pdf_path} to {txt_path}")
except Exception as e:
    print(f"Error processing {pdf_path}: {str(e)}")
