from hashlib import sha512

def passwordEncryption(password):
    ePassword = sha512(str(password).encode('utf8'))
    return ePassword.hexdigest()