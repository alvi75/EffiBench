import json
import re

def clean_html_tags(text):
    """Remove all HTML tags and unnecessary entities from the given text."""
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'&nbsp;', ' ', text)  # Replace &nbsp; with space
    text = re.sub(r'\s+', ' ', text).strip()  # Remove excessive whitespace and newlines
    return text

def process_description(description):
    """Clean the description and format it with [START] and [END]."""
    cleaned_text = clean_html_tags(description)

    # Find the position of "Example 1"
    example_idx = cleaned_text.find("Example 1")

    if example_idx != -1:
        # Place [START] at the beginning and [END] before "Example 1"
        description_cleaned = f"[START] {cleaned_text[:example_idx].strip()} [END] {cleaned_text[example_idx:].strip()}"
    else:
        description_cleaned = f"[START] {cleaned_text} [END]"

    # Extract description_context: Content between [START] and [END]
    description_context = description_cleaned.split("[START]")[1].split("[END]")[0].strip()

    return description_cleaned, description_context

def process_json_file(input_file, output_file):
    """Read JSON file, process descriptions, and save the modified data."""
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        if "description" in item:
            item["description_cleaned"], item["description_context"] = process_description(item["description"])

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Processed JSON saved to {output_file}")

# Run the script
input_file = "../data/dataset.json"  # Change this to your input JSON file
output_file = "../data/processed_dataset.json"  # Change this to your desired output file
process_json_file(input_file, output_file)
