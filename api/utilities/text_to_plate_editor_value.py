text = """
หากเรามีจำนวนเต็มบวกจำนวนหนึ่ง Factorial ของจำนวนนั้นกคือผลคูณของจำนวนเต็มทั้งหมดตั้งแต่ตัวเอง ไปจนถึง 1 (ในทางคณิตศาสตร์จะได้สัญลักษณ์ `!` แทน Factorial) เช่น `5! = 5 x 4 x 3 x 2 x 1 = 120`
สำหรับ `0! = 1` (เป็นสมบัติพิเสษ)

ให้เขียนโปรแกรมที่รับจำนวนเต็มบวก และแสดงผลของของ Factorial ของค่านั้น

<u>ข้อมูลนำเข้า</u>  
มีบรรทัดเดียว เป็นจำนวนเต็มที่*ไม่ใช่*จำนวนเต็มลบ **n**

<u>ข้อมูลส่งออก</u>  
แสดงผลของของ Factorial ของค่า n

## Example 1
<pre class="output">
n: _0_
1
</pre>

## Example 2
<pre class="output">
n: _5_
120
</pre>

## Example 3
<pre class="output">
n: _10_
3628800
</pre>
"""
import json

class Increment:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1
        return str(self.count)
    
def cutBetween(text:str,delimeter:str):
    gets = []
    start = -1
    for i in range(len(text)-len(delimeter)+1):
        if text[i:i+len(delimeter)] == delimeter and start == -1:
            start = i
        elif text[i:i+len(delimeter)] == delimeter and start != -1:
            gets.append(text[start+len(delimeter):i])
            start = -1
    return [i for i in gets if i!='']

def enchantMarkdown(text):
    bold = cutBetween(text,"**")
    italic = [i for i in cutBetween(text,"*") if i not in bold]

    children = []
    
    for txt in text.split("*"):
        if len(txt) > 2  and txt[0] == "*" and txt[-1] == "*":
            children.append({ "text": txt, "bold": True })
        elif txt in italic:
            children.append({ "text": txt, "italic": True })
        else:
            children.append({ "text": txt })

    return [i for i in children if i!='']


def transformToEditorValue(text:str):
    plateValue = []
    count = Increment()

    # Description
    descriptionChildren = []
    description = [txt for txt in text.split("<u>")[0].split("\n") if txt != "" and txt != "\n"]
    for txt in description:
        for j in enchantMarkdown(txt):
            descriptionChildren.append(j)
        descriptionChildren.append({ "text": "\n" })
    plateValue.append({
        "id": count.inc(),
		"type": "p",
		"children": descriptionChildren
    })

    # Input Output
    inputText =   [j for j in [i for i in text.split('<u>') if i.startswith('ข้อมูลนำเข้า')][0].split("\n") if j != '' and j != '\n'][1:]
    outputText =  [j for j in [i for i in text.split('<u>') if i.startswith('ข้อมูลส่งออก')][0].split("\n") if j != '' and j != '\n'][1:]

    for i in range(len(outputText)):
        if '## Example' in outputText[i]:
            outputText = outputText[:i]
            break

    inputPlate = []
    for txt in inputText:
        for j in enchantMarkdown(txt):
            inputPlate.append(j)
        inputPlate.append({ "text": "\n" })

    outputPlate = []
    for txt in outputText:
        for j in enchantMarkdown(txt):
            inputPlate.append(j)
        outputPlate.append(*enchantMarkdown(txt))
        outputPlate.append({ "text": "\n" })


    plateValue.append({
		"id": count.inc(),
		"type": "p",
		"children": [
            { "text": "ข้อมูลนำเข้า ", "underline": True },
            *inputPlate,
            { "text": "ข้อมูลส่งออก ", "underline": True },
            *outputText
        ]
    })

    # print(inputText)
    # print(outputText)

    # Example
    examples = [example[17:-2] for example in text.split('pre')[1:] if example[17:-2] != '' and example[17:-2] != '\n']
    
    for i in range(len(examples)):
        plateValue.append({ "id": count.inc(), "type": "h2", "children": [{ "text": f"Example {i+1}" }] })
        plateValue.append({
        "type": "code_block",
        "children": [
            {
                "type": "code_line",
                "children": [{ "text": text } for text in examples[i].split('\n') if text != '' and text != '\n'],
                "id": count.inc()
            }
        ]
    })
    
    # Write on file in one line
    with open('output.json','w') as f:
        f.write(json.dumps(plateValue))
        



transformToEditorValue(text)

