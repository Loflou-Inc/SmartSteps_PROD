import os
import glob

# Directory with Jane's text files
directory = "G:/My Drive/Deftech/SmartSteps/smart_steps_ai/personas/Jane"

# List all text files
txt_files = glob.glob(f"{directory}/*.txt")

# Create a summary file
with open(f"{directory}/jane_summary.txt", "w", encoding="utf-8") as summary_file:
    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        
        # Try to read the file
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Write a section header and the first 1000 characters to the summary
                summary_file.write(f"\n\n{'='*80}\n")
                summary_file.write(f"FILE: {filename}\n")
                summary_file.write(f"{'='*80}\n\n")
                summary_file.write(content[:2000] + "...\n")
                
            print(f"Successfully read: {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            
    print(f"Created summary file: jane_summary.txt")
