import pdfplumber
import os
import glob

# Path to Jane PDFs
pdf_dir = "G:/My Drive/Deftech/SmartSteps/smart_steps_ai/personas/Jane"

# Get all PDFs in the directory
pdf_files = glob.glob(f"{pdf_dir}/*.pdf")

for pdf_path in pdf_files:
    # Create output file path
    txt_path = pdf_path.replace(".pdf", ".txt")
    
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
            
            print(f"Successfully converted {os.path.basename(pdf_path)} to {os.path.basename(txt_path)}")
    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {str(e)}")
