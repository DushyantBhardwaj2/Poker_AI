import pokerkit

content = """
variant = 'NT'
ante_trimming_status = false
antes = [0, 120000, 0, 0, 0]
blinds_or_straddles = [40000, 80000, 0, 0, 0]
min_bet = 80000
starting_stacks = [7380000, 2500000, 5110000, 10170000, 4545000]
actions = ['d dh p1 7s4s', 'd dh p2 Js8h', 'd dh p3 Td8c', 'd dh p4 6d5h', 'd dh p5 Qh7h', 'p3 f', 'p4 cbr 170000', 'p5 f', 'p1 f', 'p2 cc', 'd db JcTs2d', 'p2 cc', 'p4 cbr 140000', 'p2 cc', 'd db As', 'p2 cc', 'p4 cbr 325000', 'p2 cc', 'd db Qs', 'p2 cc', 'p4 cbr 600000', 'p2 cc', 'p4 sm 6d5h', 'p2 sm Js8h']
players = ['Matthew Ashton', 'Kristopher Tong', 'James Obst', 'Talal Shakerchi', 'Brian Rast']
"""

hh = pokerkit.HandHistory.loads(content)
print(f"First pass:")
for i, (state, action) in enumerate(hh.state_actions):
    if i < 3: print(f"Action {i}: {action}")

print(f"\nSecond pass:")
for i, (state, action) in enumerate(hh.state_actions):
    if i < 3: print(f"Action {i}: {action}")
