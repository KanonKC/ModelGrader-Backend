from hashlib import sha512
import regex as re
import random
import string
from typing import Callable, Dict, Iterable, List, TypeVar

T = TypeVar('T')
K = TypeVar('K')

def passwordEncryption(password):
    ePassword = sha512(str(password).encode('utf8'))
    return ePassword.hexdigest()

def formParser(querydict):
    dct = dict(querydict)
    return {i:dct[i][0] for i in dct}

def uploadTopic(instance,filename):
    return f"topics/{filename}"

def uploadProblemImportPDF(instance,filename):
    return f"import-pdfs/{filename}"

def regexMatching(regex:str,code:str)->bool:
    code = ";".join([i.strip() for i in code.split("\n") if i != ""])
    return re.search(regex, code)

def extract_bearer_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def generate_random_string(length=7):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def check_pdf(file) -> bool:
    """
    Check if the uploaded file is a PDF.
    Returns True if it is a PDF, False otherwise.
    """
    if not file.name.lower().endswith('.pdf'):
        return False
    
    header = file.read(4)
    file.seek(0)
    if header != b'%PDF' or file.size >= 2.5 * 1024 * 1024:
        return False
    return True

def group_by(iterable: Iterable[T], key_fn: Callable[[T], K]) -> Dict[K, List[T]]:
    """
    Group items of an iterable into a dict of lists keyed by key_fn(item).

    Replaces the copy-pasted `grouped = {}; for x in qs: grouped.setdefault(...)`
    pattern used across repositories to turn a single batched queryset into a
    per-parent-id lookup (e.g. testcases per problem_id, members per group_id).
    """
    grouped: Dict[K, List[T]] = {}
    for item in iterable:
        grouped.setdefault(key_fn(item), []).append(item)
    return grouped

def ERROR_TYPE_TO_STATUS(errorType: str) -> int:
    errorMap = {
        "unauthorized": 401,
        "not_found": 404,
        "forbidden": 403,
        "bad_request": 400,
        "internal_error": 500,
        "unknown": 500,
    }

    return errorMap.get(errorType, 500)
    