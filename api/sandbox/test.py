# from grader import *

# code = """
# x = input()
# file = open(f"./api/sandbox/section1/{x}",'r')
# print(file.read())
# """

# exptected = """Hello
# This is a sample text."""

# result = grading(
#     1,
#     code,
#     [
#         "./media/testfile/sample_text_1.txt",
#         "./media/testfile/sample_text_2.txt"
#     ],
#     [
#         "sample_text_1.txt",
#         "sample_text_2.txt"
#     ],
#     [
#         "Hello",
#         exptected
#     ],
#     1.5
# )
# print(result)

# # target = """Hello 
# # aaaa"""

# # print({'a':target,'b':target.strip()})

s = input("Input text: ")
n = int(input("N: "))

for i in range(len(s)):
    if i % n == 0 and i != 0:
        print()
    print(s[i],end="")