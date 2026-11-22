"""P7-v1: bounded ridge residual for observation-only continuation utility.

The training target is a declared *synthetic counterfactual rollout oracle*, not
observed game's chosen-action outcome. No hidden board, opponent policy ID or
future selected action may enter the online feature vector.
"""
from __future__ import annotations
import math
import random


FEATURES = ("bias", "unknown_fraction", "own_material_count", "visible_enemy_count")
SAFE_FIELDS = {"side", "view", "own_history_sha256", "legal_attempts",
               "visible_enemy_count", "visible_square_count"}


def featurize(online):
    if set(online) != SAFE_FIELDS:
        raise ValueError("P7 rejects non-predecision online feature")
    view = online["view"]
    if not isinstance(view, str) or len(view) != 64:
        raise ValueError("invalid observation")
    side = online["side"]
    if side not in ("white", "black"):
        raise ValueError("invalid side")
    own = ("PNBRQK" if side == "white" else "pnbrqk")
    material_count = sum(c in own for c in view) / 16
    visible_enemy = online["visible_enemy_count"] / 16
    if not 0 <= material_count <= 1 or not 0 <= visible_enemy <= 1:
        raise ValueError("invalid piece count")
    return (1.0, view.count("?") / 64, material_count, visible_enemy)


def solve_linear(matrix, vector):
    n = len(vector)
    aug = [list(row) + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) <= 1e-12:
            raise ValueError("singular regularized design")
        aug[pivot], aug[col] = aug[col], aug[pivot]
        scale = aug[col][col]
        aug[col] = [v / scale for v in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [a - factor * b for a, b in zip(aug[row], aug[col])]
    return [aug[i][-1] for i in range(n)]


def fit(rows, ridge=1):
    if not rows or ridge <= 0:
        raise ValueError("positive ridge and nonempty records required")
    d = len(rows[0][0])
    xtx = [[0.0] * d for _ in range(d)]
    xty = [0.0] * d
    for features, baseline, target in rows:
        if len(features) != d or any(not math.isfinite(x) for x in features):
            raise ValueError("finite fixed-size online vector required")
        if not -1 <= baseline <= 1 or not -1 <= target <= 1:
            raise ValueError("bounded simulated continuation values required")
        y = target - baseline
        for j in range(d):
            xty[j] += features[j] * y
            for k in range(d):
                xtx[j][k] += features[j] * features[k]
    for j in range(d):
        xtx[j][j] += ridge if j else ridge * 0.1
    return solve_linear(xtx, xty)


def predict(features, baseline, coefficients, max_residual=0.3):
    residual = sum(f * w for f, w in zip(features, coefficients))
    correction = min(max(residual, -max_residual), max_residual)
    return min(1.0, max(-1.0, baseline + correction))


def mse(rows, coefficients=None):
    return sum(((baseline if coefficients is None else predict(x, baseline, coefficients))
                - target) ** 2 for x, baseline, target in rows) / len(rows)


def mock_view(rng):
    own_count = rng.randrange(6, 17)
    enemy_count = rng.randrange(1, 10)
    unknown_count = rng.randrange(10, 43)
    chars = "P" * own_count + "p" * enemy_count + "?" * unknown_count
    chars += "-" * (64 - len(chars))
    chars = list(chars)
    rng.shuffle(chars)
    view = "".join(chars)
    return {"side": "white", "view": view,
            "own_history_sha256": "0" * 64, "legal_attempts": ["a2a3"],
            "visible_enemy_count": enemy_count, "visible_square_count": 64 - unknown_count}


def dataset(seed, n, intercept=0.02):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        x = featurize(mock_view(rng))
        baseline = rng.uniform(-0.25, 0.25)
        # Synthetic counterfactual continuation policy's analytical target.
        # The *model does not receive* the later generated target or noise.
        truth = baseline + intercept - 0.16 * x[1] + 0.11 * x[2] - 0.04 * x[3]
        target = min(1, max(-1, truth + rng.gauss(0, 0.015)))
        rows.append((x, baseline, target))
    return rows


def trial(seed=719):
    train = dataset(seed, 500)
    development = dataset(seed + 1, 160)
    holdout = dataset(seed + 2, 160)
    candidates = (0.02, 0.2, 2.0, 20.0)
    trained = {alpha: fit(train, alpha) for alpha in candidates}
    chosen = min(candidates, key=lambda a: mse(development, trained[a]))
    residual = mse(holdout, trained[chosen])
    base = mse(holdout)
    rng = random.Random(seed + 33)
    permuted = list(train)
    targets = [y for _, _, y in permuted]
    rng.shuffle(targets)
    permuted = [(x, b, t) for (x, b, _), t in zip(permuted, targets)]
    shuffled = fit(permuted, chosen)
    random_target = mse(holdout, shuffled)
    assert residual < base
    assert residual < random_target
    return {"primary_metric": "held-out synthetic continuation-target MSE",
            "ridge": chosen, "holdout_mse": residual,
            "baseline_mse": base, "shuffled_target_mse": random_target,
            "coefficients": dict(zip(FEATURES, trained[chosen])),
            "n_train": len(train), "n_development": len(development),
            "n_untouched_holdout": len(holdout),
            "no_counterfactual_from_observed_action": True,
            "limitations": "Synthetic analytical counterfactual teacher, NOT Stockfish or on-policy FoW outcome. Distinct game-group and true replay experiments remain."}
