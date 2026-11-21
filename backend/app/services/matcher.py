from rapidfuzz.fuzz import ratio
import re

def clean(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def clean_phone(s: str) -> str:
    return re.sub(r'\D', '', s or '')[-10:]

def str_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return ratio(clean(a), clean(b))

def phone_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 100.0 if clean_phone(a) == clean_phone(b) else 0.0

def compare(a: dict, b: dict) -> dict:
    name = str_score(a.get('full_name'), b.get('full_name'))
    email = str_score(a.get('email'), b.get('email'))
    phone = phone_score(a.get('phone'), b.get('phone'))
    address = str_score(a.get('address'), b.get('address'))
    dob = 100.0 if a.get('date_of_birth') and a.get('date_of_birth') == b.get('date_of_birth') else 0.0
    # exact email or phone boosts strongly
    score = round(name*0.35 + email*0.25 + phone*0.25 + address*0.10 + dob*0.05, 2)
    return {"score": score, "name_score": round(name,2), "email_score": round(email,2), "phone_score": phone, "address_score": round(address,2), "dob_score": dob}
