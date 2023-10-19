import subprocess

class TestcaseResult:

    RUNTIME_STATUS = [
        'OK',
        'ERROR',
        'TIMEOUT'
    ]

    def __init__(self,input:str,output:str,runtime_status:RUNTIME_STATUS) -> None:
        self.input = input
        self.output = output
        self.runtime_status = runtime_status

class RunningResult:
    def __init__(self,testcases:list[TestcaseResult]) -> None:
        self.testcases = testcases
        self.has_error = False
        self.has_timeout = False

        for item in testcases:
            if item.runtime_status in 'ERROR':
                self.has_error = True
            elif item.runtime_status == 'TIMEOUT':
                self.has_timeout = True

    def __str__(self) -> str:
        result = ''
        for item in self.testcases:
            result += f'{item.input}\n-------\n{item.output}\nRuntime Status: {item.runtime_status}\n\n'
        return result

class GradingResult:

    def normalize(self,string:str) -> str:
        return string.replace('\r','')

    def __init__(self,running_result:RunningResult,expected_output:str) -> None:
        
        self.testcases = self.running_result.testcases
        self.has_error = self.running_result.has_error
        self.has_timeout = self.running_result.has_timeout

        if running_result.has_error or running_result.has_timeout or (self.normalize(expected_output) != self.normalize(self.testcases.output)):
            self.is_passed = False
        else:
            self.is_passed = True

    def __str__(self) -> str:
        if self.has_error:
            return 'E'
        elif self.has_timeout:
            return 'T'
        elif not self.is_passed:
            return '-'
        else:
            return 'P'
class Program:
    def __init__(self,source_code:str) -> None:
        self.source_code = source_code

    def import_testcases(self,testcases:list[str],section:int) -> None:
        for i in range(len(testcases)):
            with open(f'./api/sandbox/section{section}/testcases/{i}.txt','w') as f:
                f.write(testcases[i])

    def setup_environment(self,testcases:list[str],section:int) -> None:
        self.import_testcases(testcases,section)
        
    def generate_output(self,testcases:list[str],time_limit_ms:int,section:int) -> list[RunningResult]:
        pass

    def grading(self,expected_outputs:list[str],time_limit_ms:int,section:int) -> list[GradingResult]:
        running_result = self.generate_output(expected_outputs,time_limit_ms,section)
        testcases = running_result.testcases

        grading_result:list[GradingResult] = []
        
        for case in testcases:
            grading_result.append(GradingResult(case,expected_outputs[testcases.index(case)]))
        
        return grading_result

class PythonProgram(Program):
    def __init__(self,source_code:str) -> None:
        super().__init__(source_code)

    def setup_environment(self, testcases: list[str], section: int) -> None:
        super().setup_environment(testcases, section)
        with open(f'./api/sandbox/section{section}/runner.py','w') as f:
            f.write(self.source_code)

    def generate_output(self,testcases:list[str],time_limit_ms:int,section:int) -> RunningResult:
        result = []
        self.setup_environment(testcases,section)
        print("Call this")
        for i in range(len(testcases)):
            try:
                runner = subprocess.check_output(['python',f'./api/sandbox/section{section}/runner.py'],stdin=open(f'./api/sandbox/section{section}/testcases/{i}.txt','r'),stderr=subprocess.DEVNULL,timeout=float(time_limit_ms/1000))
                result.append(TestcaseResult(testcases[i],runner.decode(),'OK'))
            except subprocess.CalledProcessError:
                result.append(TestcaseResult(testcases[i],None,'ERROR'))
            except subprocess.TimeoutExpired:
                result.append(TestcaseResult(testcases[i],None,'TIMEOUT'))
        return RunningResult(result)

class CppProgram(Program):
    def __init__(self,source_code:str) -> None:
        super().__init__(source_code)

    def setup_environment(self, testcases: list[str], section: int) -> None:
        super().setup_environment(testcases, section)
        with open(f'./api/sandbox/section{section}/runner.cpp','w') as f:
            f.write(self.source_code)
        subprocess.check_output(['g++',f'./api/sandbox/section{section}/runner.cpp','-o',f'./api/sandbox/section{section}/runner.exe'],stderr=subprocess.DEVNULL)

    def generate_output(self,testcases:list[str],time_limit_ms:int,section:int) -> RunningResult:
        result = []
        for i in range(len(testcases)):
            try:
                runner = subprocess.check_output([f'./api/sandbox/section{section}/runner.exe'],stdin=open(f'./api/sandbox/section{section}/testcases/{i}.txt','r'),stderr=subprocess.DEVNULL,timeout=float(time_limit_ms/1000))
                result.append(TestcaseResult(testcases[i],runner.decode(),'OK'))
            except subprocess.CalledProcessError:
                result.append(TestcaseResult(testcases[i],None,'ERROR'))
            except subprocess.TimeoutExpired:
                result.append(TestcaseResult(testcases[i],None,'TIMEOUT'))
        return RunningResult(result)
    

def forgiveableFormat(string:str)->str:
    return string.replace('\r','')

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
                graded_result[i]['is_passed'] = True
                continue
            else:
                score += '-'
        elif graded_result[i]['runtime_status'] == 'TIMEOUT':
            score += 'T'
        else:
            score += 'E'
        graded_result[i]['is_passed'] = False
    
    return score, graded_result 



adder = '''
x = int(input("x: "))
y = int(input("y: "))
print(x+y)
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

prog = PythonProgram(adder)
result = prog.generate_output(test,1500,1)
grade = prog.grading(['3','70','4'],1500,1)
print("RESULT",grade)
# print(grading(adder,test,['x: y: 3\r\n','x: y: 70\r\n','x: y: 4\r\n']))