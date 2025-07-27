from microprojects import calc


def test_add():
    assert calc("1+1") == 2


def test_div():
    assert calc("10 / 6") == 1.666667


def test_scale_0():
    assert calc("10.0 / 6.0", scale=0) == 1


def test_scale_3():
    assert calc("10 / 6", scale=3) == 1.667


def test_sin_pi():
    assert calc("sin(pi)") == 0


def test_mul():
    assert calc("5 * 2") == 10
    assert calc("5 x 2") == 10


def test_hex_num():
    assert calc("0xFF") == 255
    assert calc("0 x 3") == 0


def test_bitand():
    assert calc("bitand (0xFE, 0x2e)") == 46


def test_bitor():
    assert calc("bitor(9,2)") == 11


def test_base_hex():
    assert calc("192") == 0xC0


def test_ncr():
    assert calc("ncr(49,6)") == 13983816


def test_max():
    assert calc("max( 5,2,3,1)") == 5
