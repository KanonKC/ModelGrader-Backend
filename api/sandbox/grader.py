import subprocess

"""
Usecases:
- Create problem
- Update code

- Update testcases
- Submit problem
"""

def forgiveableFormat(string:str)->str:
    return string.replace('\r','')
    # return string

class RuntimeResult:

    RUNTIME_STATUS = [
        'OK',
        'ERROR',
        'TIMEOUT'
    ]

    def __init__(self,input:str,output:str,runtime_status:RUNTIME_STATUS) -> None:
        self.input = input
        self.output = output
        self.runtime_status = runtime_status

    def __iter__(self):
        yield 'input',self.input
        yield 'output',self.output
        yield 'runtime_status',self.runtime_status

    def __str__(self) -> str:
        return str(dict(self))

class GradingResult:
    def __init__(self,input:str,output:str,runtime_status:RuntimeResult.RUNTIME_STATUS,expected_output:str,is_passed:bool) -> None:
        self.input = input
        self.output = output
        self.runtime_status = runtime_status
        self.expected_output = expected_output
        self.is_passed = is_passed

    def __iter__(self):
        yield 'input',self.input
        yield 'output',self.output
        yield 'runtime_status',self.runtime_status
        yield 'expected_output',self.expected_output
        yield 'is_passed',self.is_passed

    def __str__(self) -> str:
        return str(dict(self))


class RuntimeResultList:
    def __init__(self,runtimeResult:list[RuntimeResult]) -> None:
        self.data = runtimeResult
        self.has_error = len([res for res in runtimeResult if res.runtime_status == "ERROR"]) > 0
        self.has_timeout = len([res for res in runtimeResult if res.runtime_status == "TIMEOUT"]) > 0
        self.runnable = not (self.has_error or self.has_timeout)

    def getResult(self) -> list[dict]:
        return [dict(i) for i in self.data]

class GradingResultList:
    def __init__(self,gradingResult:list[GradingResult]) -> None:
        self.data = gradingResult
        self.has_error = len([res for res in gradingResult if res.runtime_status == "ERROR"]) > 0
        self.has_timeout = len([res for res in gradingResult if res.runtime_status == "TIMEOUT"]) > 0
        self.runnable = not (self.has_error or self.has_timeout)
        self.is_passed = len([res for res in gradingResult if res.is_passed]) == len(gradingResult)

    def getResult(self) -> list[dict]:
        return [dict(i) for i in self.data]
        

class ProgramGrader:
    def __init__(self,code:str,testcases:list[str],section:int,timeout:float) -> None:
        self.code = code
        self.testcases = testcases
        self.section = section
        self.timeout = timeout

    def import_testcases(self) -> None:
        for i in range(len(self.testcases)):
            with open(f'./api/sandbox/section{self.section}/testcases/{i}.txt','w') as f:
                f.write(self.testcases[i])

    def import_source_code(self) -> None:
        pass

    def setup(self) -> None:
        self.import_testcases()
        self.import_source_code()
        
    def compile(self) -> None:
        pass

    def runtime(self) -> list[RuntimeResult]:
        pass
        
    def generate_output(self) -> RuntimeResultList:
        try:
            self.setup()
            self.compile()
            return RuntimeResultList(self.runtime())
        except Exception as e:
            return RuntimeResultList([RuntimeResult(testcase,None,"ERROR") for testcase in self.testcases])

    def grading(self,expected_output:list[str]) -> GradingResultList:
        try:
            self.setup()
            self.compile()
            runtime_result = self.runtime()
        except:
            runtime_result = [RuntimeResult(testcase,None,"ERROR") for testcase in self.testcases]

        if len(runtime_result) != len(expected_output):
            raise Exception("Length of expected output and runtime result is not equal")
        
        grading_result = []
        for i in range(len(runtime_result)):

            is_passed = False
            output = None

            if runtime_result[i].runtime_status == "OK":
                
                output = runtime_result[i].output
                if forgiveableFormat(runtime_result[i].output) == forgiveableFormat(expected_output[i]):
                    is_passed = True
                else:
                    runtime_result[i].runtime_status = "FAILED"
            
            grading_result.append(GradingResult(
                 runtime_result[i].input,
                 output,
                 runtime_result[i].runtime_status,
                 expected_output[i],
                 is_passed
            ))

        return GradingResultList(grading_result)

class PythonGrader(ProgramGrader):

    def import_source_code(self) -> None:
        with open(f'./api/sandbox/section{self.section}/runner.py','w') as f:
            f.write(self.code)

    def runtime(self) -> list[RuntimeResult]:
        
        result = []
        
        for i in range(len(self.testcases)):
            try:
                runner = subprocess.check_output([
                    'python',f'./api/sandbox/section{self.section}/runner.py'],
                    stdin=open(f'./api/sandbox/section{self.section}/testcases/{i}.txt',
                    'r'
                ),stderr=subprocess.DEVNULL,timeout=float(self.timeout))
                result.append(RuntimeResult(self.testcases[i],runner.decode(),"OK"))
            except subprocess.CalledProcessError as e:
                result.append(RuntimeResult(self.testcases[i],None,"ERROR"))
            except subprocess.TimeoutExpired:
                result.append(RuntimeResult(self.testcases[i],None,"TIMEOUT"))

        return result

class CGrader(ProgramGrader):

    def import_source_code(self) -> None:
        with open(f'./api/sandbox/section{self.section}/runner.c','w') as f:
            f.write(self.code)

    def compile(self) -> None:
        subprocess.check_output(['gcc',f'./api/sandbox/section{self.section}/runner.c','-o',f'./api/sandbox/section{self.section}/runner.exe'],stderr=subprocess.DEVNULL)

    def runtime(self) -> list[RuntimeResult]:
            
            result = []
            
            for i in range(len(self.testcases)):
                try:
                    runner = subprocess.check_output([
                        f'./api/sandbox/section{self.section}/runner.exe'],
                        stdin=open(f'./api/sandbox/section{self.section}/testcases/{i}.txt',
                        'r'
                    ),stderr=subprocess.DEVNULL,timeout=float(self.timeout))
                    result.append(RuntimeResult(self.testcases[i],runner.decode(),"OK"))
                except subprocess.CalledProcessError:
                    result.append(RuntimeResult(self.testcases[i],None,"ERROR"))
                except subprocess.TimeoutExpired:
                    result.append(RuntimeResult(self.testcases[i],None,"TIMEOUT"))
    
            return result

class CppGrader(ProgramGrader):
    def import_source_code(self) -> None:
        with open(f'./api/sandbox/section{self.section}/runner.cpp','w') as f:
            f.write(self.code)

    def compile(self) -> None:
        subprocess.check_output(['g++',f'./api/sandbox/section{self.section}/runner.cpp','-o',f'./api/sandbox/section{self.section}/runner.exe'],stderr=subprocess.DEVNULL)

    def runtime(self) -> list[RuntimeResult]:
            
            result = []
            
            for i in range(len(self.testcases)):
                try:
                    runner = subprocess.check_output([
                        f'./api/sandbox/section{self.section}/runner.exe'],
                        stdin=open(f'./api/sandbox/section{self.section}/testcases/{i}.txt',
                        'r'
                    ),stderr=subprocess.DEVNULL,timeout=float(self.timeout))
                    result.append(RuntimeResult(self.testcases[i],runner.decode(),"OK"))
                except subprocess.CalledProcessError:
                    result.append(RuntimeResult(self.testcases[i],None,"ERROR"))
                except subprocess.TimeoutExpired:
                    result.append(RuntimeResult(self.testcases[i],None,"TIMEOUT"))
    
            return result


Grader:list[ProgramGrader] = {
    "python": PythonGrader,
    "c": CGrader,
    "cpp": CppGrader
}

# adder = '''
# x = int(input("x: "))
# y = int(input("y: "))
# print(x-y)
# '''

# adderC = r'''
# #include <stdio.h>

# int main() {
#     int a,b;
#     scanf("%d",&a);
#     scanf("%d",&b);
#     printf("%d\n",a-b);
#     return 0;
# }
# '''

# adderCpp = r'''
# #include <iostream>
# using namespace std;

# int main() {
#     int a,b;
#     cin >> a;
#     cin >> b;

#     cout << a - b << "\n";    
# }
# '''

# test = [
# '''1
# 2
# ''',
# '''52
# 18
# ''',
# '''9
# -5
# '''
# ]

# pyresult = ["x: y: -1\r\n","x: y: 34\r\n","x: y: 14\r\n"]
# cresult = ["-1\r\n","34\r\n","14\r\n"]

# grader = Grader['python']
# result = grader(adder,test,1,1.5).grading(pyresult)
# print(result.getResult())