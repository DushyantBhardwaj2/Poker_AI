from data_loader import PHHParser
import pandas as pd

parser = PHHParser()
file_path = r"poker-hand-histories\data\wsop\2023\43\5\00-02-07.phh"
records = list(parser.parse_phh_file(file_path))

print(f"Total records: {len(records)}")
if records:
    df = pd.DataFrame(records)
    print(df[['player_id', 'street', 'is_showdown', 'hole_cards', 'bet_amount']])
else:
    print("No records found")
