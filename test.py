import requests

desc = '''# Time Converter

เขียนโปรแกรมที่แปลงเวลาหน่วยวินาที ให้เป็นชั่วโมง นาที และวินาที เช่น 3661 วินาทีก็คือ 1 ชั่วโมง 1 นาที 1 วินาที

<u>ข้อมูลนำเข้า</u>  
มีแค่บรรทัดเดียวเป็นเวลาในหน่วยวินาที เป็นจำนวนเต็มบวก

<u>ข้อมูลส่งออก</u>  
แสดงผลลัพธ์ออกมาในหน่วยชั่วโมง นาที และวินาที

## Example 1
<pre class="output">
second(s): _3661_
3661 => 1 hour(s): 1 minute(s): 1 second(s)
</pre>

## Example 2
<pre class="output">
second(s): _1235_
1235 => 0 hour(s): 20 minute(s): 35 second(s)
</pre>

## Example 2
<pre class="output">
second(s): _9843_
9843 => 2 hour(s): 44 minute(s): 3 second(s)
</pre>
'''

solution = '''
s = int(input("second(s): "))

m = (s//60)%60
h = (s//3600)

print(f"{s} => {h} hour(s): {m} minute(s): {s%60} second(s)")
'''

body = {
    "title": "Time Converter",
    "language": "py",
    "description": desc,
    "solution": solution,
    "testcases": ["360","3661","120"]
}

submit_body = {
    'submission_code': solution
}

# x = requests.post('http://localhost:8000/api/problems',json=body)

# x = requests.get('http://localhost:8000/api/problems/3')

x = requests.post('http://localhost:8000/api/problems/7/submission',json=submit_body)
print(x.json())