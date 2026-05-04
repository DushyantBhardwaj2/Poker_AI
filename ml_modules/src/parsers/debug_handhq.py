import pokerkit
import re

file_path = r"poker-hand-histories\data\handhq\ABS-2009-07-01_2009-07-23_1000NLH_OBFU\10\abs NLH handhq_1-OBFUSCATED.phhs"

with open(file_path, 'r') as f:
    content = f.read()

# Try to split by [n] pattern
hands = re.split(r'\[\d+\]', content)
hands = [h.strip() for h in hands if h.strip()]

print(f"Found {len(hands)} hand blocks")

for i, h in enumerate(hands[:5]):
    try:
        hh = pokerkit.HandHistory.loads(h)
        print(f"Hand {i} parsed successfully: {hh.variant}")
    except Exception as e:
        print(f"Hand {i} failed: {e}")
