from .ClosedLoopSimGuidedPartitioner import ClosedLoopSimGuidedPartitioner
import numpy as np


class ClosedLoopUnGuidedPartitioner(ClosedLoopSimGuidedPartitioner):
    def __init__(self, dynamics, num_partitions=16, make_animation=False, show_animation=False):
        ClosedLoopSimGuidedPartitioner.__init__(self, dynamics=dynamics, make_animation=make_animation, show_animation=show_animation)

    def check_if_partition_within_sim_bnds(
        self, output_range, output_range_sim
    ):
        return False

    def get_sampled_out_range_guidance(
        self, input_constraint, propagator, t_max=5, num_samples=1000
    ):
        return None

    def squash_down_to_one_range(self, output_range_sim, M):
        # Same as ClosedLoopSimGuided's method, but ignore output_range_sim

        # (len(M)+1, t_max, n_states, 2)
        tmp = np.array([m[-1] for m in M])
        mins = np.min(tmp[..., 0], axis=0)
        maxs = np.max(tmp[..., 1], axis=0)
        return np.stack([mins, maxs], axis=2)
