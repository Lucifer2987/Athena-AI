import ast, pathlib

# 1. Syntax + encoding check on runtime.py
src = pathlib.Path('energyplus/runtime.py').read_text(encoding='utf-8')
ast.parse(src)
bad = [hex(ord(c)) for c in src if ord(c) > 127]
print('Encoding:', 'CLEAN' if not bad else 'BAD: ' + str(set(bad)))

# 2. Verify config.py exports all required names
config_src = pathlib.Path('energyplus/config.py').read_text(encoding='utf-8')
required = ['ENERGYPLUS_DIR', 'EXAMPLE_FILE', 'WEATHER_FILE', 'OUTPUT_DIR', 'PLANNING_INTERVAL']
for name in required:
    status = 'YES' if name in config_src else 'MISSING'
    print(f'  config.py has {name}: {status}')

print()
print('SYNTAX OK')
