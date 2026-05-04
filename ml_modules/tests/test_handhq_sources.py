from data_loader import PHHParser
from pathlib import Path

parser = PHHParser()
data_dir = Path('poker-hand-histories/data/handhq')
dirs = [d for d in data_dir.iterdir() if d.is_dir()]

print(f"{'Directory':<60} | {'Records':<10}")
print("-" * 75)

for d in dirs:
    f = next(d.rglob('*.phhs'), None)
    if f:
        try:
            recs = list(parser.parse_phh_file(str(f)))
            print(f"{d.name:<60} | {len(recs):<10}")
        except Exception as e:
            print(f"{d.name:<60} | Error: {e}")
