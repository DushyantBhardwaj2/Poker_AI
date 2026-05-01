import pokerkit
from data_loader import PHHParser
import time

parser = PHHParser()
file_path = 'poker-hand-histories/data/handhq/ABS-2009-07-01_2009-07-23_1000NLH_OBFU/10/abs NLH handhq_1-OBFUSCATED.phhs'
start = time.time()
recs = list(parser.parse_phh_file(file_path))
print(f"Parsed {len(recs)} records in {time.time()-start:.2f}s")
if recs:
    print("Sample record:", recs[0])
else:
    print("No records parsed!")
