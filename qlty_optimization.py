import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def solve_qlty_nudge(qty, fat_pre, target_low, target_high, max_step=2):
    
    n = len(qty)
    qty = np.asarray(qty, dtype=float)
    fat_pre = np.asarray(fat_pre, dtype=int)


    # Bounds: x_i within ±max_step of fat_pre_i
    lb = np.concatenate([fat_pre - max_step, np.zeros(n)])
    ub = np.concatenate([fat_pre + max_step, np.full(n, max_step)])
    bounds = Bounds(lb, ub)

    integrality = np.ones(2 * n)  # all integer

    # Objective: minimize total absolute adjustment -> minimize sum(d_i)
    c = np.concatenate([np.zeros(n), np.ones(n)])

    constraints = []

    # 1) Weighted sum target: target_low <= sum(qty_i * x_i) <= target_high
    A_target = np.concatenate([qty, np.zeros(n)])
    constraints.append(LinearConstraint(A_target, target_low, target_high))

    # 2) Linearize d_i >= |x_i - fat_pre_i| via two constraints each:
    #    x_i - d_i <= fat_pre_i
    #    -x_i - d_i <= -fat_pre_i
    for i in range(n):
        row1 = np.zeros(2 * n); row1[i] = 1; row1[n + i] = -1
        constraints.append(LinearConstraint(row1, -np.inf, fat_pre[i]))
        row2 = np.zeros(2 * n); row2[i] = -1; row2[n + i] = -1
        constraints.append(LinearConstraint(row2, -np.inf, -fat_pre[i]))

    res = milp(c, constraints=constraints, integrality=integrality, bounds=bounds)

    if not res.success:
        return None  # trigger escalation tier here

    x = np.round(res.x[:n]).astype(int)
    return x,res