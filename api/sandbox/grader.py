import subprocess

def checker(code:str,testcases:list,timeout=1.5)->dict:
    result = []
    hasError = False
    hasTimeout = False
    for i in range(len(testcases)):
        with open(f'./api/sandbox/testcases/{i}.txt','w') as f:
            f.write(testcases[i])
    
    with open('./api/sandbox/runner.py','w') as f:
        f.write(code)

    for i in range(len(testcases)):
        try:
            runner = subprocess.check_output(['python','./api/sandbox/runner.py'],stdin=open(f'./api/sandbox/testcases/{i}.txt','r'),stderr=subprocess.DEVNULL,timeout=float(timeout))
            result.append({'input':testcases[i],'output':runner.decode(),'runtime_result':'OK'})
        except subprocess.CalledProcessError:
            hasError = True
            result.append({'input':testcases[i],'output':None,'runtime_result':'ERROR'})
        except subprocess.TimeoutExpired:
            hasTimeout = True
            result.append({'input':testcases[i],'output':None,'runtime_result':'TIMEOUT'})

    return {'result':result,'has_error':hasError,'has_timeout':hasTimeout}
    

def grading(code:str,input:list,output:list,timeout=1.5)->str:
    score = ''
    graded = checker(code,input,timeout)
    graded_result = graded['result']

    for i in range(len(output)):
        if graded_result[i]['runtime_result'] == 'OK':
            if graded_result[i]['output'] == output[i]:
                score += 'P'
            else:
                score += '-'
        elif graded_result[i]['runtime_result'] == 'TIMEOUT':
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