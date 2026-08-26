"""Regression tests for the hand-history parser that builds the training set.

These use one hand written inline rather than a file from the corpus, because the
corpus is gitignored and this needs to run on a clean clone. The hand is a real
one (Talal Shakerchi barrelling four streets with 6d5h against Kristopher Tong's
Js8h) chosen because it makes the two bugs below unmistakable: the aggressor has
nothing and the caller has top pair, so misattributing the bets inverts the only
label the model cares about.

Both bugs came from the same misreading of the pokerkit API. It pairs each action
with the state *after* that action was applied, so:

  - `state.actor_index` points at whoever acts next. Reading it as "who did this"
    moved every bet onto the following player, and since hole cards are joined
    back on player_id, each bet inherited the wrong player's cards.
  - `state.pots` holds only chips already gathered. Outstanding bets sit in
    `state.bets` until the street closes, so the preflop pot looked like the ante
    alone. `rel_bet_size` and `spr` are both computed against pot_before, so a
    170k raise into a 240k pot was recorded as a raise into 120k.
"""

import pytest

from src.parsers.data_loader import PHHParser

# Ante 120k from p2, blinds 40k/80k. p3 folds, p4 raises to 170k, p5 and p1 fold,
# p2 calls, and p4 then bets flop, turn and river with 6d5h on JcTs2d As Qs.
HAND = """
variant = 'NT'
ante_trimming_status = false
antes = [0, 120000, 0, 0, 0]
blinds_or_straddles = [40000, 80000, 0, 0, 0]
min_bet = 80000
starting_stacks = [7380000, 2500000, 5110000, 10170000, 4545000]
actions = ['d dh p1 7s4s', 'd dh p2 Js8h', 'd dh p3 Td8c', 'd dh p4 6d5h', 'd dh p5 Qh7h', 'p3 f', 'p4 cbr 170000', 'p5 f', 'p1 f', 'p2 cc', 'd db JcTs2d', 'p2 cc', 'p4 cbr 140000', 'p2 cc', 'd db As', 'p2 cc', 'p4 cbr 325000', 'p2 cc', 'd db Qs', 'p2 cc', 'p4 cbr 600000', 'p2 cc', 'p4 sm 6d5h', 'p2 sm Js8h']
players = ['Matthew Ashton', 'Kristopher Tong', 'James Obst', 'Talal Shakerchi', 'Brian Rast']
"""

AGGRESSOR = "Talal Shakerchi"
CALLER = "Kristopher Tong"

# Pot facing each of p4's four bets: 120k ante + 40k + 80k, then the running
# total as p2 calls each street.
EXPECTED = [
    {"street": 0, "pot_before": 240000.0, "bet_amount": 170000.0},
    {"street": 1, "pot_before": 500000.0, "bet_amount": 140000.0},
    {"street": 2, "pot_before": 780000.0, "bet_amount": 325000.0},
    {"street": 3, "pot_before": 1430000.0, "bet_amount": 600000.0},
]


@pytest.fixture
def records(tmp_path):
    hand_file = tmp_path / "hand.phh"
    hand_file.write_text(HAND, encoding="utf-8")
    # failed_log_path is redirected so a parse failure does not append to the
    # developer's failed_parses.log in the working directory.
    parser = PHHParser(failed_log_path=str(tmp_path / "failed.log"))
    return list(parser.parse_phh_file(str(hand_file)))


def test_only_voluntary_bets_and_raises_are_recorded(records):
    """Folds, calls, showdowns and the dealer's board deals are not actions."""
    assert len(records) == 4


def test_each_bet_is_credited_to_the_player_who_made_it(records):
    """The bug: these four came back as the next player to act instead."""
    assert [r["player_id"] for r in records] == [AGGRESSOR] * 4
    assert CALLER not in {r["player_id"] for r in records}


def test_hole_cards_follow_the_bettor(records):
    """Every bet must carry the bettor's cards, not the caller's.

    This is the assertion that matters most. 6d5h on JcTs2dAsQs is a bluff and
    Js8h is top pair, so getting this wrong does not blur the labels, it flips
    them: the dataset would claim top pair fired four barrels.
    """
    for record in records:
        assert record["hole_cards"] == ["6d", "5h"]


def test_the_pot_includes_bets_not_yet_gathered(records):
    """pot_before is what the bettor was pricing against, blinds included."""
    assert [r["pot_before"] for r in records] == [e["pot_before"] for e in EXPECTED]


def test_bet_amounts_and_streets_are_read_from_the_action(records):
    assert [r["bet_amount"] for r in records] == [e["bet_amount"] for e in EXPECTED]
    assert [r["street"] for r in records] == [e["street"] for e in EXPECTED]


def test_relative_bet_size_is_sane(records):
    """The feature actually fed to the model, derived from the two fields above.

    engineer_features_v3 computes bet_amount / pot_before. Understating the pot
    inflated it, which for the preflop raise here meant 1.42x pot instead of
    0.71x - the difference between a standard raise and a wild one.
    """
    preflop = records[0]
    assert preflop["bet_amount"] / preflop["pot_before"] == pytest.approx(0.708, abs=0.001)


def test_the_showdown_flag_is_set_when_cards_are_shown(records):
    assert all(r["is_showdown"] for r in records)


def test_starting_stack_belongs_to_the_bettor(records):
    """Indexed by the same actor, so it was wrong in the same way. SPR uses it."""
    for record in records:
        assert record["starting_stack"] == 10170000.0


def test_hand_ids_are_stable_and_unique_per_hand(records):
    assert len({r["hand_id"] for r in records}) == 1
    assert records[0]["hand_id"].endswith("_000000")


def test_a_non_nlhe_hand_is_skipped(tmp_path):
    """The dataset is hold'em only; other variants must not leak in."""
    stud = HAND.replace("variant = 'NT'", "variant = 'FT'")
    hand_file = tmp_path / "stud.phh"
    hand_file.write_text(stud, encoding="utf-8")

    parser = PHHParser(failed_log_path=str(tmp_path / "failed.log"))
    assert list(parser.parse_phh_file(str(hand_file))) == []
    assert parser.skipped_variant_count == 1


def test_an_unreadable_file_is_logged_not_raised(tmp_path):
    """Ingestion runs over thousands of files and must not stop at a bad one."""
    log = tmp_path / "failed.log"
    parser = PHHParser(failed_log_path=str(log))

    assert list(parser.parse_phh_file(str(tmp_path / "does-not-exist.phh"))) == []
    assert parser.failed_count == 1
    assert "does-not-exist.phh" in log.read_text(encoding="utf-8")
