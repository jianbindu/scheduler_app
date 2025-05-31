import os
import re
from collections import defaultdict

def find_duplicate_dash_outputs(root_dir="."):
    # (component_id, property) -> list of (filename, lineno, code)
    output_map = defaultdict(list)
    # 支持 dash.callback 和 dash.dependencies.Output
    output_pattern = re.compile(r'Output\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]')

    for folder, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(".py"):
                path = os.path.join(folder, fname)
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for idx, line in enumerate(lines):
                    # 简单行内搜索，不处理多行嵌套很深的情况
                    for m in output_pattern.finditer(line):
                        cid, prop = m.groups()
                        output_map[(cid, prop)].append((path, idx + 1, line.strip()))

    # 打印重复的输出
    has_dup = False
    for k, lst in output_map.items():
        if len(lst) > 1:
            has_dup = True
            print(f"\n[重复输出] Output({k[0]!r}, {k[1]!r}) 出现 {len(lst)} 次:")
            for fname, lineno, code in lst:
                print(f"  {fname}:{lineno}: {code}")
    if not has_dup:
        print("未检测到重复的 Output 输出！")

if __name__ == "__main__":
    # 修改为你的 Dash 项目根目录，比如 "./scheduler_app"
    find_duplicate_dash_outputs(".")
