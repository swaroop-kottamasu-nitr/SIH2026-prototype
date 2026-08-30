import os
import re

suspicious_patterns = [
    re.compile(r'AIza[0-9A-Za-z-_]{35}'),
    re.compile(r'sk-[0-9A-Za-z]{20,}'),
    re.compile(r'(?i)(api_key|secret_key|private_key)\s*=\s*[\'"][a-zA-Z0-9_\-]{16,}[\'"]')
]

found = []
for root, dirs, files in os.walk(os.path.join('..', 'frontend', 'src')):
    for f in files:
        if f.endswith(('.js', '.jsx', '.ts', '.tsx', '.json', '.css', '.html')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fl:
                content = fl.read()
                for pat in suspicious_patterns:
                    matches = pat.findall(content)
                    if matches:
                        found.append((path, matches))

if not found:
    print('SECURITY CHECK PASSED: Zero API keys or secrets in frontend source code.')
else:
    print('SECURITY ALERT: Found secrets:', found)
