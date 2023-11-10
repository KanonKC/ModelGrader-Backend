from hashlib import sha512
import regex as re

def passwordEncryption(password):
    ePassword = sha512(str(password).encode('utf8'))
    return ePassword.hexdigest()

def formParser(querydict):
    dct = dict(querydict)
    return {i:dct[i][0] for i in dct}

def uploadTopic(instance,filename):
    return f"topics/{filename}"

def regexMatching(regex:str,code:str)->bool:
    code = ";".join([i.strip() for i in code.split("\n") if i != ""])
    print(bool(re.search(regex, code)))
    return re.search(regex, code)