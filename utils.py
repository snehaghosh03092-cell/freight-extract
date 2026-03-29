import time
import re
import json
import random
from groq import RateLimitError

from prompts import build_prompt
from schemas import EmailExtraction
from pydantic import ValidationError

def get_null_output(email_id):
    return {
        "id": email_id,
        "product_line": None,
        "incoterm": None,
        "origin_port_code": None,
        "origin_port_name": None,
        "destination_port_code": None,
        "destination_port_name": None,
        "cargo_weight_kg": None,
        "cargo_cbm": None,
        "is_dangerous": False
    }

def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end + 1])
        except Exception:
            return None
    return None

def extract_wait_time(error_str, default=300):
    match = re.search(r"try again in (\d+)m([\d.]+)s", error_str)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return int(minutes * 60 + seconds)
    return default

def retry_llm_call(func, max_retries=3, base_delay=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = (
                "rate_limit" in error_str
                or "429" in error_str
                or isinstance(e, RateLimitError)
            )
            is_timeout = "timeout" in error_str
            if not (is_rate_limit or is_timeout):
                raise
            if attempt == max_retries - 1:
                return None
            wait_time = extract_wait_time(str(e), default=None)
            if wait_time is None:
                wait_time = base_delay * (2 ** attempt)
            wait_time += random.uniform(0, 2)
            print(f"Retry {attempt+1}: sleeping {round(wait_time,2)}s")
            time.sleep(wait_time)

def process_email(email, llm_call, port_ref):
    email_id = email.get("id")
    try:
        prompt = build_prompt(
            email["id"],
            email.get("subject", ""),
            email.get("body", ""),
            port_ref
        )
        res = retry_llm_call(lambda: llm_call(prompt))
        if not res:
            return get_null_output(email_id)

        content = res.choices[0].message.content
        raw = safe_json_parse(content)
        if not raw:
            return get_null_output(email_id)
        try:
            validated = EmailExtraction(**raw)
            return validated.model_dump()
        except ValidationError as e:
            return get_null_output(email_id)
    except Exception as e:
        print(f"Error: {email_id} -> {e}")
        return get_null_output(email_id)