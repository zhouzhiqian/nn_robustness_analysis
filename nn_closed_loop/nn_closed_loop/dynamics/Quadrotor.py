from .Dynamics import ContinuousTimeDynamics
import numpy as np


class Quadrotor(ContinuousTimeDynamics):
    def __init__(self):

        g = 9.8  # m/s^2

        At = np.zeros((6, 6))
        At[0][3] = 1
        At[1][4] = 1
        At[2][5] = 1

        bt = np.zeros((6, 3))
        bt[3][0] = g
        bt[4][1] = -g
        bt[5][2] = 1

        ct = np.zeros((6,))
        ct[-1] = -g

        # u_limits = None
        u_limits = np.array(
            [
                [-np.pi / 9, np.pi / 9],
                [-np.pi / 9, np.pi / 9],
                [0, 2 * g],
            ]
        )

        dt = 0.1

        super().__init__(At=At, bt=bt, ct=ct, u_limits=u_limits, dt=dt)

        self.cmap_name = "tab20"
