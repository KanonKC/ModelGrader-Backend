import os
import subprocess

def grading(candidate_code:str,solution_code:str,testcases:list)->str:
    result = ''
    testcases.append('9\n10')
    with open('./api/sandbox/candidate.py','w') as f:
        f.write(candidate_code)
    with open('./api/sandbox/solution.py','w') as f:
        f.write(solution_code)
    for i in range(len(testcases)):
        f = open(f'./api/sandbox/testcases/{i}.txt','w')
        f.write(testcases[i])
        f.close
    
    for i in range(len(testcases)):
        candidate = subprocess.run(['python','./api/sandbox/candidate.py','<',f'./api/sandbox/testcases/{i}.txt'],shell=True,capture_output=True)
        solution = subprocess.run(['python','./api/sandbox/solution.py','<',f'./api/sandbox/testcases/{i}.txt'],shell=True,capture_output=True)
        if candidate.returncode == 1:
            result += 'E'
        elif candidate.stdout.decode() == solution.stdout.decode():
            result += 'P'
        else:
            result += '-'
    return result[:-1]