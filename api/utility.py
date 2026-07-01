from hashlib import sha512
import regex as re
import random
import string

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
    