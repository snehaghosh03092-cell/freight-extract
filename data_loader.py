import json

def load_emails(path="emails.json"):
    with open(path, "r") as f:
        return json.load(f)

def load_ports(path="port_codes_ref.json"):
    with open(path, "r") as f:
        return json.load(f)