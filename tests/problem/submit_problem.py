import requests

code = '''
n = int(input("N: "))
print(n+1)
'''

body = {
    "submission_code": code
}

result = requests.post("http://localhost:8000/api/problems/4/1",data=body)
print(result.text)