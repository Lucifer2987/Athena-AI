import pandas as pd
import pathlib

# 1. Check CSV
f = pathlib.Path('logs/simulation_log.csv')
print('=== CSV CHECK ===')
if f.exists():
    df = pd.read_csv(f, encoding='utf-8')
    print('Rows:', len(df))
    print(df[['step','tool','confidence','reasoning']].head(15).to_string())
    print()
    na_tools   = (df['tool'].str.upper() == 'N/A').sum()
    zero_conf  = (pd.to_numeric(df['confidence'], errors='coerce').fillna(0) <= 0).sum()
    old_fallback = df['reasoning'].str.contains('Fallback action due to LLM', na=False).sum()
    print('N/A tools        :', na_tools)
    print('Zero confidence  :', zero_conf)
    print('Old fallback msg :', old_fallback)
else:
    print('CSV NOT FOUND')

# 2. Delivery artifacts
print()
print('=== DELIVERY ARTIFACTS ===')
for p in ['logs/baseline_building.idf', 'logs/modified_building_notes.txt']:
    pp = pathlib.Path(p)
    if pp.exists():
        print(f'  {p}: EXISTS ({pp.stat().st_size:,} bytes)')
    else:
        print(f'  {p}: MISSING')
