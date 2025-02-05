import os
import json
import random
import spacy
import openai
from nltk.corpus import wordnet
from parrot import Parrot
from datetime import datetime
from tqdm import tqdm

# Load spaCy for NLP-based modifications
nlp = spacy.load("en_core_web_sm")

# Initialize Parrot for sentence rephrasing
parrot = Parrot()

# Set OpenAI API Key (Ensure it is exported: export OPENAI_API_KEY="your-key")
openai.api_key = os.getenv("OPENAI_API_KEY")

class NLPerturbator:
    def __init__(self, frequency=0.3):
        """Initialize the NLPerturbator with a frequency parameter (default: 30% perturbation)."""
        self.frequency = frequency

    def perturb_text(self, text, perturbation_type):
        """Apply a specific perturbation type."""
        perturbations = {
            "E6": self._synonym_substitution,
            "P1": self._rephrase_sentence,
            "P2": self._declarative_to_interrogative,
            "E1": self._keyboard_typo,
            "D3": self._delete_determiners
        }
        return perturbations[perturbation_type](text) if perturbation_type in perturbations else text

    def extract_natural_language_part(self, markdown_text):
        """Extracts only the first two sentences from markdown_description before 'Example 1'."""
        if "Example 1" in markdown_text:
            prefix, _ = markdown_text.split("Example 1", 1)
        else:
            prefix = markdown_text  # Fallback if "Example 1" is not found

        return prefix.strip()

    def _synonym_substitution(self, text):
        """[E6] Synonym Substitution (Excludes bold words `**word**`)."""
        words = text.split()
        for i in range(len(words)):
            if random.random() < self.frequency and not (words[i].startswith("**") and words[i].endswith("**")):
                synonyms = set()
                for syn in wordnet.synsets(words[i]):
                    for lemma in syn.lemmas():
                        synonyms.add(lemma.name().replace("_", " "))
                if synonyms:
                    words[i] = random.choice(list(synonyms))
        return " ".join(words)

    def _rephrase_sentence(self, text):
        """[P1] Rephrasing Sentence."""
        if random.random() < self.frequency:
            paraphrases = parrot.augment(input_phrase=text, use_gpu=False)
            if paraphrases:
                return paraphrases[0][0]
        return text

    def _declarative_to_interrogative(self, text):
        """[P2] Convert a declarative sentence into a question."""
        if random.random() < self.frequency:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": f"Convert this statement into a question: {text}"}]
            )
            return response["choices"][0]["message"]["content"].strip()
        return text

    def _keyboard_typo(self, text):
        """[E1] Introduce random keyboard typos."""
        qwerty_mapping = {
            'q': ['w', 'a'], 'w': ['q', 'e', 's'], 'e': ['w', 'r', 'd'], 'r': ['e', 't', 'f'],
            't': ['r', 'y', 'g'], 'y': ['t', 'u', 'h'], 'u': ['y', 'i', 'j'], 'i': ['u', 'o', 'k'],
            'o': ['i', 'p', 'l'], 'p': ['o', 'l'], 'a': ['q', 's', 'z'], 's': ['a', 'w', 'd', 'x'],
            'd': ['s', 'e', 'f', 'c'], 'f': ['d', 'r', 'g', 'v'], 'g': ['f', 't', 'h', 'b'],
            'h': ['g', 'y', 'j', 'n'], 'j': ['h', 'u', 'k', 'm'], 'k': ['j', 'i', 'l'],
            'l': ['k', 'o'], 'z': ['a', 'x'], 'x': ['z', 's', 'c'], 'c': ['x', 'd', 'v'],
            'v': ['c', 'f', 'b'], 'b': ['v', 'g', 'n'], 'n': ['b', 'h', 'm'], 'm': ['n', 'j']
        }
        perturbed_text = list(text)
        for i in range(len(perturbed_text)):
            if perturbed_text[i].lower() in qwerty_mapping and random.random() < self.frequency:
                perturbed_text[i] = random.choice(qwerty_mapping[perturbed_text[i].lower()])
        return "".join(perturbed_text)

    def _delete_determiners(self, text):
        """[D3] Removes determiners (e.g., 'the', 'a', 'an')."""
        doc = nlp(text)
        tokens = [token.text for token in doc if token.pos_ != "DET" or random.random() >= self.frequency]
        return " ".join(tokens)

def backup_dataset(dataset_path):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = dataset_path.replace(".json", f"_backup_{timestamp}.json")
    os.system(f"cp {dataset_path} {backup_path}")
    print(f"Backup created: {backup_path}")

def apply_perturbations(dataset_path):
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    pert = NLPerturbator(frequency=0.3)
    perturbations = {
        "P1": "dataset_P1.json",
        "P2": "dataset_P2.json",
        "E6": "dataset_E6.json",
        "E1": "dataset_E1.json",
        "D3": "dataset_D3.json"
    }

    for pert_type, file_name in perturbations.items():
        perturbed_dataset = []
        print(f"Applying {pert_type} perturbation...")
        for entry in tqdm(dataset, desc=f"Processing {pert_type}", unit="entry"):
            perturbed_entry = entry.copy()
            original_text = pert.extract_natural_language_part(entry["markdown_description"])
            perturbed_text = pert.perturb_text(original_text, pert_type)
            perturbed_entry["markdown_description"] = entry["markdown_description"].replace(original_text, perturbed_text)
            perturbed_dataset.append(perturbed_entry)

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(perturbed_dataset, f, indent=4)

        print(f"Perturbed dataset saved: {file_name}\n")

if __name__ == "__main__":
    dataset_path = "../data/dataset.json"
    backup_dataset(dataset_path)
    apply_perturbations(dataset_path)
