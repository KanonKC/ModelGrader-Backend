from hashlib import sha512

def passwordEncryption(password):
    ePassword = sha512(str(password).encode('utf8'))
    return ePassword.hexdigest()

def formParser(querydict):
    dct = dict(querydict)
    return {i:dct[i][0] for i in dct}

def uploadTopic(instance,filename):
    return f"topics/{filename}"