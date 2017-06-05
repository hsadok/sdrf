import unittest
from mmmalloc.allocators.hyperplane_allocation import allocate


def check_allocation(desire, output):
    def utility(desire, output):
        if output < desire < 0:
            return False
        if output < 0 <= desire:
            return False
        return True

    if sum(output) != 0:
        return False

    if not all(utility(d, o) for (d, o) in zip(desire, output)):
        return False

    return True


class TestAllocate(unittest.TestCase):
    def test_lack_resource_int_reputation(self):  # sum a > 0
        desire = [1, 3, 2, -1, -2, 1]
        reputation = [-10, -3, -5, 2, 4, 12]

        output = allocate(desire, reputation)
        self.assertEqual(output, [1, 0, 2, -1, -2, 0])
        self.assertEqual(desire, [1, 3, 2, -1, -2, 1])
        self.assertEqual(reputation, [-10, -3, -5, 2, 4, 12])

        desire = [-1, 3, -2, 1, 2, -1]
        reputation = [10, 3, 5, -2, -4, -12]

        output = allocate(desire, reputation)
        self.assertEqual(output, [-1, 1, -2, 1, 2, -1])

        desire = [-1, 3, -2, 3, 3, -1]
        reputation = [10, 3, 7, -4, -4, -12]

        output = allocate(desire, reputation)
        self.assertEqual(output, [-1, 0, -2, 2, 2, -1])

    def test_lack_resources_float_reputation(self):
        desire = [1, 3, 2, 2, -3, 1, -5, 3, 0]
        reputation = [-6.2, -3.1, -3.1, -2.2, 8.6, 12.2, -4.3, 6.0, -7.9]
        output = allocate(desire, reputation)
        self.assertEqual(output, [1, 3, 2, 2, -3, 0, -5, 0, 0])

        desire = [1, 3, 3, 2, -3, 1, -5, 3, 0]
        reputation = [-6.2, -3.1, -3.0, -2.2, 8.5, 12.2, -4.3, 6.0, -7.9]
        output = allocate(desire, reputation)
        self.assertEqual(output, [1, 3, 2, 2, -3, 0, -5, 0, 0])

        desire = [1, 3, 3, 2, -3, 1, -5, 3, 0]
        reputation = [-6.2, -3.1, -3.1, -2.2, 8.6, 12.2, -4.3, 6.0, -7.9]
        output = allocate(desire, reputation)
        self.assertIn(output, [[1, 3, 2, 2, -3, 0, -5, 0, 0],
                               [1, 2, 3, 2, -3, 0, -5, 0, 0]])

        desire = [-983, -495, 0, -17, -94, -146, -1, 1089]
        reputation = [-2.58127908e+02, -1.26568030e+02, 0.0, -4.46406352e+00,
                      -2.46836453e+01, -4.60910629e+00, 6.32071646e-01,
                      6.07617756e+03]
        output = allocate(desire, reputation)
        self.assertEqual(output, [-350, -481, 0, -17, -94, -146, -1, 1089])

        desire = [-983, -2478, -23049, -495, -17, -94, 0, -147, 31, -10224]
        reputation = [-2.39549965e+01, -6.03870615e+01, -4.69976046e+02,
                      -9.48788737e+00, -4.14277662e-01, -2.29071178e+00,
                      0.00000000e+00, -3.58228331e+00, -2.43692742e-02,
                      5.70117634e+02]
        output = allocate(desire, reputation)
        self.assertEqual(output, [0, 0, 0, 0, 0, 0, 0, 0, 31, -31])

    def test_lack_consumer(self):  # sum a < 0
        desire = [1, -3, 2, -1, -2, 1]
        reputation = [-10, -3, -5, 2, 4, 12]

        output = allocate(desire, reputation)
        self.assertEqual(output, [1, -1, 2, -1, -2, 1])

    def test_efficient(self):  # sum a = 0
        desire = [1, -3, 2, -1, -2, 3]
        reputation = [-10, -3, -5, 2, 4, 12]

        output = allocate(desire, reputation)
        self.assertEqual(output, [1, -3, 2, -1, -2, 3])

    def test_big(self):
        desire = [-983, -2478, -23049, -495, -17, -94, 0, -146, -1, 21714,
                  -4156, -107, 0, -24364, -396, -1031, -4468,
                  -63, -1, -6790, -1901, -63, -21547, -1, -1660, -606159,
                  -27252, -20732, -253, -32, -47341, -313, -866,
                  -625, -18742, 0, -4526, -701, -27973, -247116, -2222, -2707,
                  -5, -329, 0, -313, -157, -10023, -625,
                  -2375, -1283, -3, -1, -18750, -78924, 4839, -1675, -3708,
                  -57, -446, -9623, -46034, -583, -5440,
                  -52682, 27, 0, -2539, -2151, -4, -853, -2089, 38439, -61239,
                  -2907, -625, -3685, -1199, -7, -1783, 0,
                  -2005, -837, -844, -313, -711743, 0, -12722, -1251, -1683,
                  -35, -1594, -563, 80981, -21695, -11220,
                  -1850, -2, -313, -56723]

        reputation = [-1.93418703e+02, -3.93776940e+02, -1.71944642e+03,
                      -9.92155235e+01, -3.48096398e+00,
                      -1.92476832e+01, 0.00000000e+00, -2.89384122e+01,
                      1.07687710e+00, 3.91272692e+03, -5.76192989e+02,
                      -2.19095968e+01, 0.00000000e+00, -1.74725053e+03,
                      -8.10859845e+01, -2.02159471e+02,
                      -6.07374341e+02, -1.29000430e+01, 9.51397825e-01,
                      -8.22002247e+02, 1.33160704e+03,
                      -1.29000430e+01, -1.68463791e+03, -2.04762587e-01,
                      -2.92670853e+02, -3.15038309e+03,
                      -1.80375115e+03, -1.66254973e+03, -5.18049345e+01,
                      -6.55240279e+00, -2.06030690e+03,
                      -6.40906898e+01, -1.16099946e+02, -1.27976617e+02,
                      -2.78623320e+02, 0.00000000e+00,
                      -6.13140177e+02, -1.42393315e+02, -1.81751219e+03,
                      5.84595627e+01, -3.63496168e+02,
                      -4.20323983e+02, -1.02381294e+00, -6.73668912e+01,
                      0.00000000e+00, -6.40906898e+01,
                      -3.21477262e+01, -1.09025955e+03, -1.27976617e+02,
                      -3.81739503e+02, -2.40312687e+02,
                      -7.85605411e-01, -2.04762587e-01, -1.59807063e+03,
                      -2.31330586e+03, 1.04958658e+03,
                      -2.94675630e+02, -5.30342912e+02, -1.16714675e+01,
                      -9.13241139e+01, 2.25649242e+04,
                      2.94179960e+03, -1.19376588e+02, -7.01088546e+02,
                      -2.04086538e+03, 5.52858985e+00, 0.00000000e+00,
                      1.44522306e+03, -3.54861273e+02, -8.19050349e-01,
                      -1.70284453e+02, -3.46550085e+02,
                      7.87086909e+03, -2.19543445e+03, -4.42964565e+02,
                      -1.27976617e+02, -5.27925210e+02,
                      -2.28089817e+02, -1.43333811e+00, -3.08828070e+02,
                      0.00000000e+00, -3.36796774e+02,
                      -1.67353840e+02, -1.68636088e+02, -6.40906898e+01,
                      -3.15038321e+03, 0.00000000e+00,
                      1.46365618e+02, -2.35687084e+02, -2.95733551e+02,
                      -7.16669055e+00, -2.83755101e+02,
                      -1.15281337e+02, 4.47185258e+03, -1.68825538e+03,
                      -1.14602352e+03, -3.17291031e+02,
                      7.13571790e-01, -6.40906898e+01, -2.15152578e+03]

        output = allocate(desire, reputation)

        self.assertEqual(output, [-983, -2478, -2588, -495, -17, -94, 0, -146,
                                  -1, 21714, -3732, -107, 0, -2561, -396,
                                  -1031, -3700, -63, -1, -3486, -1901, -63,
                                  -2623, -1, -1660, -1157, -2504, -2645, -253,
                                  -32, -2247, -313, -866, -625, -4029, 0,
                                  -3695, -701, -2490, -4366, -2222, -2707, -5,
                                  -329, 0, -313, -157, -3217, -625, -2375,
                                  -1283, -3, -1, -2710, -1994, 4839, -1675,
                                  -3708, -57, -446, -9623, -7250, -583, -3607,
                                  -2267, 27, 0, -2539, -2151, -4, -853, -2089,
                                  38439, -2112, -2907, -625, -3685, -1199, -7,
                                  -1783, 0, -2005, -837, -844, -313, -1157, 0,
                                  -4454, -1251, -1683, -35, -1594, -563, 80981,
                                  -2620, -3162, -1850, -2, -313, -2156])


if __name__ == '__main__':
    unittest.main()