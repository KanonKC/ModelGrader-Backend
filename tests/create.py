import requests

TITLE = "Prime Number 100"

DESCRIPTION = '''\
รับค่าเป็นจำนวนเต็มให้ตอบว่า จำนวนนั้นเป็นจำนวนเฉพาะหรือไม่ โดยค่าที่ใส่ไปจะไม่มีทางเกิน 100 แน่ๆ

<u>ข้อมูลนำเข้า</u>  
มีบรรทัดเดียว เป็นจำนวนเต็มบวก **n** เมื่อ 1 <= n <= 100

<u>ข้อมูลส่งออก</u>  
แสดงคำตอบออกมาว่าเป็นจำนวนเฉพาะหรือไม่

**คำใบ้**  
สำหรับจำนวนเต็มบวกที่มีค่าน้อยกว่า 100 เราสามารถเช็คจำนวนเฉพาะได้ง่ายๆ โดยการทดลองหารจำนวนเฉพาะ 2,3,5,7 จะต้องหารไม่ลงตัวเลยสักค่า

## Example 1
<pre class="output">
N: _2_
2 is a Prime Number
</pre>

## Example 2
<pre class="output">
N: _39_
39 is not a Prime Number
</pre>

## Example 3
<pre class="output">
N: _97_
97 is a Prime Number
</pre>
'''

SOLUTION = '''\
n = int(input("N: "))

if n == 1 or (n % 2 == 0 or n % 3 == 0 or n % 5 == 0 or n % 7 == 0) and (n != 2 and n != 3 and n != 5 and n != 7):
    print(f"{n} is not a Prime Number")
else:
    print(f"{n} is a Prime Number")
'''

TESTCASE = [
    '1','2','3','5','7','9','53','73','59','91','97',
]

body = {
    "title": TITLE,
    "language": "py",
    "description": DESCRIPTION,
    "solution": SOLUTION,
    "testcases": TESTCASE,
    "time_limit": 1.5
}

# submit_body = {
#     'submission_code': solution
# }

x = requests.post('http://localhost:8000/api/problems',json=body)
print(x.json())

# x = requests.get('http://localhost:8000/api/problems/3')

# x = requests.post('http://localhost:8000/api/problems/7/submission',json=submit_body)