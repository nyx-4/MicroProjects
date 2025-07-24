def lexical_analyzer(ch_stream: str, *, known_lexemes: dict = {}) -> list:
    """
    Reads the character stream and group the characters into meaningful sequences.

    Arguments:
        ch_stream (str): str to perform lexical analysis on
        known_lexemes (dict): lexical_analyzer replaces all instances of key with value,
            all known functions and consts must be passed through it.

    Returns:
        token_stream (list):
    """

    token_stream: list = []

    lexeme_begin: int = 0
    hexa: str = "0123456789ABCDEFabcdef"
    len_ch_str: int = len(ch_stream)

    while lexeme_begin < len_ch_str:
        cur_lexeme: str = ""
        is_float: bool = False
        forward: int = lexeme_begin

        if ch_stream[lexeme_begin] in " ,)":  # ignore spaces, commas and )
            lexeme_begin += 1

        # x followed by space is *
        elif ch_stream[lexeme_begin] == "x" and ch_stream[forward + 1] == " ":
            token_stream += "*"
            lexeme_begin += 1

        # 0x will fall to next elif
        elif (
            ch_stream[lexeme_begin] == "0"
            and ch_stream[forward + 1] == "x"
            and ch_stream[forward + 2] in hexa
        ):
            lexeme_begin += 1

        elif ch_stream[lexeme_begin] == "x" and ch_stream[forward + 1] in hexa:
            forward += 1  # read the x
            while forward < len_ch_str and (
                ch_stream[forward] in hexa or ch_stream[forward] == "_"
            ):
                forward += 1

            cur_lexeme = ch_stream[lexeme_begin + 1 : forward]
            token_stream += [int(cur_lexeme, base=16)]
            lexeme_begin = forward

        elif ch_stream[lexeme_begin].isdigit():  # digit means int/float
            while forward < len_ch_str:
                if ch_stream[forward].isdigit() or ch_stream[forward] == "_":
                    forward += 1
                elif ch_stream[forward] in ".eE":  # if . or e, then float
                    is_float = True
                else:
                    break

            cur_lexeme = ch_stream[lexeme_begin:forward]
            token_stream += [float(cur_lexeme) if is_float else int(cur_lexeme)]
            lexeme_begin = forward

        elif ch_stream[lexeme_begin].isalpha():  # alpha means a func/const
            # func/const can be alnum
            while forward < len_ch_str and ch_stream[forward].isalnum():
                forward += 1
            cur_lexeme = ch_stream[lexeme_begin:forward]

            # ignore all spaces after func
            while forward < len_ch_str and ch_stream[forward] == " ":
                forward += 1
            lexeme_begin = forward

            # lexeme represents a function
            if forward < len_ch_str and ch_stream[forward] == "(":
                forward += 1  # read that (
                lexeme_begin = forward

                try:
                    num_parans: int = 1
                    while num_parans > 0:
                        # one more paran to close.
                        if ch_stream[forward] == "(":
                            num_parans += 1
                        if ch_stream[forward] == ")":
                            num_parans -= 1
                        forward += 1
                except IndexError:
                    raise SyntaxError("The opening '(' is never closed")

                token_stream += [
                    [known_lexemes[cur_lexeme]]
                    + lexical_analyzer(
                        ch_stream[lexeme_begin:forward],
                        known_lexemes=known_lexemes,
                    )
                ]

                lexeme_begin = forward
            else:
                token_stream += [known_lexemes[cur_lexeme]]

        #  Anything unused by now will be copied verbatium as char
        else:
            token_stream += ch_stream[lexeme_begin]
            lexeme_begin += 1

    return token_stream


def syntax_analyzer():
    pass


def semantic_analyzer():
    pass
