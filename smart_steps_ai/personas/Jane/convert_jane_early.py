import PyPDF2

# Target a specific file
pdf_file = 'Jane-Early Trauma and Giftedness in Context.pdf'
txt_file = 'Jane-Early.txt'

try:
    with open(pdf_file, 'rb') as file:
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Get number of pages
        num_pages = len(pdf_reader.pages)
        print(f"File has {num_pages} pages")
        
        # Extract text from each page
        with open(txt_file, 'w', encoding='utf-8') as output_file:
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                output_file.write(text + '\n\n')
        
        print(f"Converted {pdf_file} to {txt_file}")
except Exception as e:
    print(f"Error processing {pdf_file}: {str(e)}")
