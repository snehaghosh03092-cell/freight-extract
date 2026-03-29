import os
import json
from dotenv import load_dotenv
from tqdm import tqdm
from groq import Groq

from data_loader import load_emails, load_ports
from utils import process_email

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt):
    return client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

def main():
    emails = load_emails("emails_input.json")
    ports = load_ports("port_codes_reference.json")
    results = []
    for email in tqdm(emails, desc="Processing emails"):
        result = process_email(email, call_llm, ports)
        results.append(result)
    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)
    print("DONE → output.json created")

if __name__ == "__main__":
    main()