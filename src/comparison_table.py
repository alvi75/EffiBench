import os
import json
import pandas as pd
import random
import time
import openai
from tqdm import tqdm

# Read the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please provide your OpenAI API key.")

# File paths
original_file = "../data/processed_dataset.json"
parrot_file = "../data/dataset_P1V2.json"
gpt4_file = "../data/dataset_P1GPTv2.json"

# Load datasets
with open(original_file, "r") as f:
    original_data = json.load(f)

with open(parrot_file, "r") as f:
    parrot_data = json.load(f)

with open(gpt4_file, "r") as f:
    gpt4_data = json.load(f)

# Convert datasets to dictionaries for easy lookup (problem_idx as key)
original_dict = {item["problem_idx"]: item["description_context"] for item in original_data}
parrot_dict = {item["problem_idx"]: item["description_context"] for item in parrot_data}
gpt4_dict = {item["problem_idx"]: item["description_context"] for item in gpt4_data}

# Find common problem_ids
common_problem_ids = list(set(original_dict.keys()) & set(parrot_dict.keys()) & set(gpt4_dict.keys()))

# Randomly select 300 problem_ids
selected_ids = random.sample(common_problem_ids, 300)

# Function to call GPT-4o with rate-limit handling
def call_gpt4o(prompt):
    backoff_time = 5  # Default initial wait time

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a detailed evaluator for semantic equivalence."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response["choices"][0]["message"]["content"].strip()

        except openai.error.RateLimitError as e:
            wait_time = 10  # Default wait time
            print(f"⚠Rate limit reached! Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

        except openai.error.AuthenticationError as e:
            print(f"Authentication Error: {e}")
            return "Error: Incorrect API key"

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return "Error"

# Create a dataframe
data = []
for problem_idx in tqdm(selected_ids, desc="🔍 Evaluating descriptions"):
    original_context = original_dict[problem_idx]
    parrot_context = parrot_dict[problem_idx]
    gpt4_context = gpt4_dict[problem_idx]

    # GPT-4o prompt for evaluating GPT-4o Rephrase (dataset_P1GPT.json)
    prompt_gpt4_eval = f"""
    Compare the following two texts and determine if they are **semantically equivalent**.
    
    **Original Context:**
    {original_context}

    **Modified Context (GPT-4o Rephrase):**
    {gpt4_context}

    Respond with either "YES" (if semantically equivalent) or "NO" (if meaning is changed).
    """

    gpt4o_eval_gpt4 = call_gpt4o(prompt_gpt4_eval)

    # GPT-4o prompt for evaluating Parrot 30% Perturbation (dataset_P1.json)
    prompt_parrot_eval = f"""
    Compare the following two texts and determine if they are **semantically equivalent**.
    
    **Original Context:**
    {original_context}

    **Modified Context (Parrot 30% Perturbation):**
    {parrot_context}

    Respond with either "YES" (if semantically equivalent) or "NO" (if meaning is changed).
    """

    gpt4o_eval_parrot = call_gpt4o(prompt_parrot_eval)

    data.append([
        problem_idx, 
        original_context, 
        parrot_context, 
        gpt4_context, 
        gpt4o_eval_gpt4, 
        gpt4o_eval_parrot
    ])

# Convert to DataFrame
df = pd.DataFrame(data, columns=[
    "Problem ID", 
    "Original Description Context", 
    "Parrot 30% Perturbation", 
    "GPT-4o S.E Rephrase", 
    "GPT-4o Evaluator on GPT-4o S.E Rephrase", 
    "GPT-4o Evaluator on PARROT 30% Perturbation"
])

# Save to Excel
output_file = "../data/comparison_table.xlsx"
df.to_excel(output_file, index=False)

print(f"Comparison table saved as '{output_file}'")
