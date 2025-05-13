import os
import PyPDF2
import glob

# Get all PDF files in the current directory
pdf_files = glob.glob('*.pdf')

for pdf_file in pdf_files:
    # Create output text file name
    txt_file = pdf_file.replace('.pdf', '.txt')
    
    # Open PDF file
    try:
        with open(pdf_file, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get number of pages
            num_pages = len(pdf_reader.pages)
            
            # Extract text from each page
            with open(txt_file, 'w', encoding='utf-8') as output_file:
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    output_file.write(text + '\n\n')
            
            print(f"Converted {pdf_file} to {txt_file}")
    except Exception as e:
        print(f"Error processing {pdf_file}: {str(e)}")
