import random
from .decision import god
def benchmark_ncert(max_count=5):
    with open("mathai/ncert_data.txt", "r", encoding="utf-8") as file:
        content = file.read()
        content = content.strip().split("\n")
        random.shuffle(content)
        output = []
        count = 1
        if len(max_count) > len(content):
            max_count = len(content)
        for item in content[:max_count]:
            print(f"{count}/{max_count}")
            count += 1
            output.append((item, god(item, False)))
        print()
        for index, item in enumerate(output):
            print(f"{index+1}. {item[0]} => {item[1]}")
