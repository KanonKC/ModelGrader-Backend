import subprocess

def forgiveableFormat(string:str)->str:
    return string.replace('\r','')
    # return string

def checker(section:int,code:str,testcases:list,timeout=1.5)->dict:
    result = []
    hasError = False
    hasTimeout = False
    for i in range(len(testcases)):
        with open(f'./api/sandbox/section{section}/testcases/{i}.txt','w') as f:
            f.write(testcases[i])
    
    with open(f'./api/sandbox/section{section}/runner.py','w') as f:
        f.write(code)

    for i in range(len(testcases)):
        try:
            runner = subprocess.check_output(['python',f'./api/sandbox/section{section}/runner.py'],stdin=open(f'./api/sandbox/section{section}/testcases/{i}.txt','r'),stderr=subprocess.DEVNULL,timeout=float(timeout))
            result.append({'input':testcases[i],'output':runner.decode(),'runtime_status':'OK'})
        except subprocess.CalledProcessError:
            hasError = True
            result.append({'input':testcases[i],'output':None,'runtime_status':'ERROR'})
        except subprocess.TimeoutExpired:
            hasTimeout = True
            result.append({'input':testcases[i],'output':None,'runtime_status':'TIMEOUT'})

    return {'result':result,'has_error':hasError,'has_timeout':hasTimeout}
    

def grading(section:int,code:str,input:list,output:list,timeout=1.5)->str:
    score = ''
    graded = checker(section,code,input,timeout)
    graded_result = graded['result']

    # print(graded)
    # print(graded_result)

    for i in range(len(output)):
        if graded_result[i]['runtime_status'] == 'OK':
            if forgiveableFormat(graded_result[i]['output']) == forgiveableFormat(output[i]):
                score += 'P'
            else:
                score += '-'
        elif graded_result[i]['runtime_status'] == 'TIMEOUT':
            score += 'T'
        else:
            score += 'E'
    
    return score


adder = '''
x = int(input("x: "))
y = int(input("y: "))
print(x-y)
if x == 52:
    raise Exception
if x == 9:
    while True:
        pass
'''

test = [
'''1
2
''',
'''52
18
''',
'''9
-5
'''
]

# print(grading(adder,test,['x: y: 3\r\n','x: y: 70\r\n','x: y: 4\r\n']))