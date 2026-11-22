"""Referee-based scientific screens and their restricted negative controls."""

import pytest

from tools.stage4 import tactics


@pytest.fixture(scope="module")
def tactical_cases():
    return tactics.tactical_screens()


def test_planning_regret_uses_observation_feasible_oracle(tactical_cases):
    planning, _, _ = tactical_cases
    assert len(planning) == 4
    for fixture in planning:
        cases = list(fixture["by_root"].values())
        assert max(case["candidate_regret"] for case in cases) == 0
        # A legal policy can branch only when the next king-threat views differ.
        expected_gap = 0.5 if fixture["family"] == "incompatible-escapes" else 0
        assert max(case["fixed_action_regret"] for case in cases) == expected_gap
        assert max(case["clairvoyant_fusion_gap"] for case in cases) == expected_gap
        if expected_gap:
            assert fixture["selected_root"] != fixture["control_root"]


def test_information_value_disagrees_with_geometric_reveal(tactical_cases):
    _, information, _ = tactical_cases
    for fixture in information:
        assert set(fixture["direct_payoff"].values()) == {0}
        candidate = fixture["candidate"]
        voicers = candidate["information_only"]
        if fixture["family"] == "incompatible-escapes":
            assert voicers[candidate["selected"]]["instrumental_voi"] == 0.5
            assert voicers[fixture["square_count_control_root"]]["instrumental_voi"] == 0
        else:
            assert all(row["instrumental_voi"] == 0 for row in voicers.values())


def test_robust_mixture_improves_security_only_for_incompatible_escapes(tactical_cases):
    _, _, resolving = tactical_cases
    for fixture in resolving:
        certificate = fixture["prototype"]["certificate"]
        if fixture["family"] == "incompatible-escapes":
            assert fixture["pure_control"]["row_security_value"] == -1
            assert certificate["row_security_value"] == pytest.approx(-0.5, abs=0.01)
            assert certificate["exploitability_gap"] < 0.02
        else:
            assert fixture["pure_control"]["row_security_value"] == 0
            assert certificate["row_security_value"] == pytest.approx(0, abs=1e-6)


def test_one_turn_endgame_domain_uses_complete_referee_enumeration():
    result = tactics.endgame_screen()
    assert result["active_board_count"] + result["terminal_boards_excluded"] == 6 * 62
    assert result["information_set_count"] == 6
    assert sum(len(case["defender_hidden_worlds"]) for case in result["information_sets"]) == (
        result["active_board_count"])
    assert result["oracle_defender_replies"] > result["oracle_root_actions"] > 0
    assert result["known_worlds_with_winning_action"] > 0
    assert result["hidden_information_certifiable_actions"] == 0
    assert result["false_certificates"] == result["missing_certificates"] == 0
