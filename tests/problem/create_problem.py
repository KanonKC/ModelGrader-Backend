import requests

code = '''
n = int(input("N: "))
print(n+1)
'''

testcases = [
    "1","2","3"
]

body = {
    "title": "Plus One",
    "language": "Python",
    "description": "แสดงคำว่า 'Hello World' ออกมา",
    "solution": code,
    "testcases": testcases,
    "time_limit": 1.5
}

result = requests.post("http://localhost:8000/api/accounts/1/problems",data=body)
print(result.text)