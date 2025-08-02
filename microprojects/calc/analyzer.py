def lexical_analyzer(ch_stream: str, known_lexemes: dict = {}) -> list:
    """
    Reads the character stream and group the characters into meaningful sequences.

    Parameters:
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

        if ch_stream[lexeme_begin] == " ":  # ignore spaces
            lexeme_begin += 1

        # x followed by space is *
        elif (
            lexeme_begin + 1 < len_ch_str
            and ch_stream[lexeme_begin] == "x"
            and ch_stream[lexeme_begin + 1] == " "
        ):
            token_stream.append("*")
            lexeme_begin += 1

        # 0x will fall to next elif
        elif (
            lexeme_begin + 2 < len_ch_str
            and ch_stream[lexeme_begin] == "0"
            and ch_stream[lexeme_begin + 1] == "x"
            and ch_stream[lexeme_begin + 2] in hexa
        ):
            lexeme_begin += 1

        elif (
            lexeme_begin + 1 < len_ch_str
            and ch_stream[lexeme_begin] == "x"
            and ch_stream[lexeme_begin + 1] in hexa
        ):
            forward += 1  # read the x
            while forward < len_ch_str and (
                ch_stream[forward] in hexa or ch_stream[forward] == "_"
            ):
                forward += 1

            cur_lexeme = ch_stream[lexeme_begin + 1 : forward]
            token_stream.append(int(cur_lexeme, base=16))
            lexeme_begin = forward

        elif ch_stream[lexeme_begin].isdigit():  # digit means int/float
            while forward < len_ch_str:
                if ch_stream[forward].isdigit() or ch_stream[forward] == "_":
                    forward += 1
                # if . or e, then float
                elif ch_stream[forward] == ".":
                    is_float = True
                    forward += 1
                elif ch_stream[forward] in "eE":
                    is_float = True
                    forward += 1
                    if ch_stream[forward] == "-":
                        forward += 1
                else:
                    break

            cur_lexeme = ch_stream[lexeme_begin:forward]

            # if cur_lexeme is float, then type-cast to float
            if is_float:
                token_stream.append(float(cur_lexeme))
            else:  # else type-cast to int
                token_stream.append(int(cur_lexeme))

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

                arg_tokens: list = lexical_analyzer(
                    ch_stream[lexeme_begin : forward - 1], known_lexemes
                )
                token_stream.append([known_lexemes[cur_lexeme]] + arg_tokens)

                lexeme_begin = forward
            else:
                token_stream += [known_lexemes[cur_lexeme]]

        #  Anything unused by now will be copied verbatium as char
        else:
            token_stream.append(ch_stream[lexeme_begin])
            lexeme_begin += 1

    # Iterate once again to find unary -
    idx: int = len(token_stream) - 1
    while idx >= 0:
        if token_stream[idx] == "-" and (
            idx == 0 or type(token_stream[idx - 1]) is str
        ):
            token_stream[idx : idx + 2] = [-token_stream[idx + 1]]
        idx -= 1

    return token_stream


def shunting_yard(token_stream: list, precedence: str) -> list:
    def is_pop_needed(o1, o2) -> bool:
        return o2 != "(" and precedence.index(o2) <= precedence.index(o1)

    operator_stack: list = []
    output: list = []

    for token in token_stream:
        if token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack[-1] != "(":
                output.append(operator_stack.pop())
            operator_stack.pop()

        elif type(token) is str:  # v is operator
            while len(operator_stack) and is_pop_needed(token, operator_stack[-1]):
                output.append(operator_stack.pop())
            operator_stack.append(token)

        else:  # v is function or numeral constant
            output.append(token)

    while len(operator_stack):
        output.append(operator_stack.pop())

    return output


def solve_func(func_stream: list, precedence: str, known_lexemes: dict = {}):
    func_name = func_stream[0]
    args: tuple = ()
    forward: int = 1

    while forward < len(func_stream):
        arg_begin: int = forward
        while forward < len(func_stream) and func_stream[forward] != ",":
            forward += 1

        rev_polish = shunting_yard(func_stream[arg_begin:forward], precedence)
        args = *args, solve_rpn(rev_polish, precedence, known_lexemes)

        forward += 1

    return func_name(*args)


def solve_rpn(rev_polish: list, precedence: str, known_lexemes: dict):
    idx: int = 0

    while idx < len(rev_polish):
        if type(rev_polish[idx]) is str:
            op_func = known_lexemes[rev_polish[idx]]
            rev_polish[idx - 2 : idx + 1] = [
                op_func(rev_polish[idx - 2], rev_polish[idx - 1])
            ]
            idx -= 3  # Because three items are over-written

        elif type(rev_polish[idx]) is list:
            rev_polish[idx] = solve_func(rev_polish[idx], precedence, known_lexemes)
        idx += 1

    return rev_polish[0]
