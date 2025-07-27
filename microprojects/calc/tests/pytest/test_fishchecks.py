from microprojects import calc


def test_div_trunc():
    assert calc("3 / 2") == 1.5


def test_div_recurring():
    assert calc("10/6") == 1.666667


def test_div_ints_scale_0():
    assert calc("10 / 6", scale=0) == 1


def test_div_floor():
    assert calc("floor(10 / 6)") == 1


def test_div_scale_3():
    assert calc("10/6", scale=3) == 1.667


def test_mod_1():
    assert calc("10 % 6") == 4


def test_mod_scale_0():
    assert calc("10 % 6", scale=0) == 4


def test_mod_2():
    assert calc("23 % 7") == 2


def test_div_mul_scale_6():
    assert calc("5 / 3 * 0.3", scale=6) == 0.5


def test_div_scale_15():
    assert calc("5 / 3", scale=15) == 1.666666666666667


def test_pow_1():
    assert calc("7^2") == 49


def test_neg_num():
    assert calc("-1 + 1") == 0


def test_mul_2_neg_num():
    assert calc("-2 * -2") == 4


def test_mul_1_neg_num():
    assert calc("5 * -2") == -10


def test_div_neg_num():
    assert calc("-4 / 2") == -2


def test_mul_1_neg_num_2():
    assert calc("-4 * 2") == -8


def test_max_2args():
    assert calc("max(1,2)") == 2


def test_min_2args():
    assert calc("min(1,2)") == 1


def test_round_div():
    assert calc("round(3/2)") == 2


def test_floor_div():
    assert calc("floor(3/2)") == 1


def test_ceil_div():
    assert calc("ceil(3/2)") == 2


def test_round_neg_div():
    assert calc("round(-3/2)") == -2


def test_floor_neg_div():
    assert calc("floor(-3/2)") == -2


def test_ceil_neg_div():
    assert calc("ceil(-3/2)") == -1


def test_int_1():
    assert calc("1") == 1


def test_int_10():
    assert calc("10") == 10


def test_int_100():
    assert calc("100") == 100


def test_int_1000():
    assert calc("1000") == 1000


def test_pow_15():
    assert calc("10^15") == 1000000000000000


def test_neg_pow_14():
    assert calc("-10^14") == 100000000000000


def test_neg_pow_15():
    assert calc("-10^15") == -1000000000000000


def test_pow_of_pow():
    assert calc("3^(0.5^2)") == 1.316074


def test_neg_pow_2():
    assert calc("-2^2") == 4


def test_div_scale_0():
    assert calc("1.0 / 2.0", scale=0) == 0


def test_div_scale_0_():
    assert calc("3.0 / 2.0", scale=0) == 1


def test_pow_div():
    assert calc("10^15 / 2.0", scale=0) == 500000000000000


def test_sqrt_neg_zero():
    assert calc("sqrt(-0)") == -0


def test_hex_num():
    assert calc("0x2") == 2


def test_mul_2_x_4():
    assert calc("5 x 4") == 20


def test_mul_2x_4():
    assert calc("2x 4") == 8


def test_mul_0x_3():
    assert calc("0x 3") == 0


def test_bitand_ints():
    assert calc("bitand(0xFE, 1)") == 0


def test_bitor_ints():
    assert calc("bitor(0xFE, 1)") == 255


def test_bitxor_ints():
    assert calc("bitxor(5, 1)") == 4


def test_bitand_floats():
    assert calc("bitand(5.5, 2)") == 0


def test_bitand_float():
    assert calc("bitand(5.5, 1)") == 1


def test_bitxor_pow():
    assert calc("bitor(37 ^ 5, 255)") == 69343999


def test_log():
    assert calc("log (16, 10)") == 1.20412


def test_log2():
    assert calc("log2(8)") == 3


def test_sin_cos_2xpi():
    assert calc("sin (cos (2 x pi))") == 0.841471


def test_sin_pow():
    assert calc("sin( pow (3, 5))") == -0.890009


def test_pow_cos_pi():
    assert calc("pow (2, cos (-pi))") == 0.5


def test_pow_2cos_pi():
    assert calc("pow (2 x cos(-pi), 2)") == 4


def test_min_1args():
    assert calc("min (2)") == 2


def test_min_6args():
    assert calc("min (2, 3, 4, 5, -10, 1)") == -10


def test_min_5args():
    assert calc("min (5, 4, 3, ncr(2, 1), 5)") == 2


def test_min_5_args_ncr():
    assert calc("min (5, 4, 3, 5, ncr (2, 1))") == 2


def test_max_3ars_min_3args():
    assert calc("max (1, 2, min (3, 4, 5))") == 3


def test_max_4args_min_2args():
    assert calc("max( 1, 2, min(3, 4), 5)") == 5


def test_underscore():
    assert calc("0_1") == 1


def test_underscore_hex():
    assert calc("0x0_A") == 10


def test_underscore_add():
    assert calc("1_000 + 2_000") == 3000


def test_underscore_int():
    assert calc("1_0_0_0") == 1000


def test_underscore_floats():
    assert calc("0_0.5_0 + 0_1.0_0") == 1.5


def test_underscore_exp():
    assert calc("2e0_0_2") == 200


def test_underscore_neg_exp():
    assert calc("-0_0.5_0_0E0_0_3") == -500


def test_underscore_exp_neg():
    assert calc("20e-0_1") == 2


def test_div_sub():
    assert calc("22 / 5 - 5") == -0.6


def test_scale_0_trunc():
    assert calc("22 / 5 - 5", scale=0, scale_mode="truncate") == -0


def test_scale_0_floor():
    assert calc("22 / 5 - 5", scale=0, scale_mode="floor") == -1


def test_scale_0_round():
    assert calc("22 / 5 - 5", scale=0, scale_mode="round") == -1


def test_scale_0_ceiling():
    assert calc("22 / 5 - 5", scale=0, scale_mode="ceiling") == -0


def test_neg_div():
    assert calc("1 / 3 - 1") == -0.666667


def test_trunc():
    assert calc("1 / 3 - 1", scale_mode="truncate") == -0.666667


def test_floor():
    assert calc("1 / 3 - 1", scale_mode="floor") == -0.666667


def test_floor2():
    assert calc("2 / 3 - 1", scale_mode="floor") == -0.333333


def test_round():
    assert calc("1 / 3 - 1", scale_mode="round") == -0.666667


def test_ceiling():
    assert calc("1 / 3 - 1", scale_mode="ceiling") == -0.666667


def test_ceiling2():
    assert calc("2 / 3 - 1", scale_mode="ceiling") == -0.333333


def test_scale_6_trunc():
    assert calc("1 / 3 - 1", scale=6, scale_mode="truncate") == -0.666667


def test_scale_6_floor():
    assert calc("1 / 3 - 1", scale=6, scale_mode="floor") == -0.666667


def test_scale_6_floor2():
    assert calc("2 / 3 - 1", scale=6, scale_mode="floor") == -0.333333


def test_scale_6_round():
    assert calc("1 / 3 - 1", scale=6, scale_mode="round") == -0.666667


def test_scale_6_ceiling():
    assert calc("1 / 3 - 1", scale=6, scale_mode="ceiling") == -0.666667


def test_scale_6_ceiling2():
    assert calc("2 / 3 - 1", scale=6, scale_mode="ceiling") == -0.333333
