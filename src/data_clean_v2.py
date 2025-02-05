import json
import re

def clean_html_tags(text):
    """Remove all HTML tags and unnecessary entities from the given text."""
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'&nbsp;', ' ', text)  # Replace &nbsp; with space
    text = re.sub(r'\s+', ' ', text).strip()  # Remove excessive whitespace and newlines
    return text

def extract_description_context(markdown_description):
    """Extracts and cleans the natural language part of markdown_description before 'Example 1'."""
    if "Example 1" in markdown_description:
        prefix, _ = markdown_description.split("Example 1", 1)
    else:
        prefix = markdown_description  # Fallback if "Example 1" is not found

    cleaned_text = clean_html_tags(prefix).strip()  # Clean unwanted characters
    return cleaned_text

def process_json_file(input_file, output_file):
    """Read JSON file, process markdown_description, and save the modified data."""
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        if "markdown_description" in item:
            item["description_context"] = extract_description_context(item["markdown_description"])

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Processed JSON saved to {output_file}")

# Run the script
input_file = "../data/dataset_P1GPT.json"  # Change this to your input JSON file
output_file = "../data/dataset_P1GPTv2.json"  # Change this to your desired output file
process_json_file(input_file, output_file)
