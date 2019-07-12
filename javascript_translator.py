code_str = ""
char_list = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def show_error(_str, ln=None):
    if ln != None:
        print("[ Error at line {} ]".format(code_str.count("\n", 0, ln) + 1))
    print(_str)
    quit()


class Code:
    def __init__(self, name):
        self.name = name
        self.line = []
        self.var_list = []
        self.temp_var = 0
        self.structure = "main"
        self.class_list = []

    def tostr(self):
        _ret = ""
        for ln in self.line:
            _ret += "\n" + ln.tostr(0) + (";" if type(ln) is Value else "")
        return _ret

    def tojs(self):
        tool = Structure("__main__", [])
        self.temp_var = 0
        tool.line = self.line
        tool.tojs(self, self)
        self.line = tool.line


class Value:
    op_name = {
        "=": "assign",
        "+=": "assn_add",
        "-=": "assn_sub",
        "*=": "assn_mul",
        "/=": "assn_div",
        "==": "eq",
        "!=": "ne",
        "<=": "le",
        ">=": "ge",
        "is": "is",
        "is not": "nis",
        "in": "in",
        "not in": "nin",
        "+": "add",
        "-": "sub",
        "*": "mul",
        "/": "div",
        ">": "gt",
        "<": "lt",
        "|": "orb",
        "&": "andb",
        "**": "pow",
        "//": "quo",
        "%": "mod",
        ">>": "shr",
        "<<": "shl",
        "and": "and",
        "or": "or",
        "^": "xorb"
    }

    def __init__(self, _op, _param):
        self.op = _op
        self.param = _param

    def tostr(self, indent=0):
        if self.op == "string":
            _ret = self.param[0][1:len(self.param[0]) - 1]
            _ret = _ret.replace("\\", "\\\\")
            _ret = _ret.replace("\n", "\\n")
            _ret = _ret.replace("\t", "\\t")
            _ret = _ret.replace("\'", "\\'")
            _ret = _ret.replace("\"", "\\\"")
            return "\"{}\"".format(_ret)
        elif self.op in "var,number".split(","):
            return self.param[0]
        elif self.op == "list":
            return " " * 4 * indent + "[{}]".format(",".join([x.tostr(0) for x in self.param]))
        elif self.op == "tuple":
            return " " * 4 * indent + "({})".format(",".join([x.tostr(0) for x in self.param]))
        elif self.op == "listcomp":
            return " " * 4 * indent + "[{} for {} in {}]".format(self.param[0].tostr(0), self.param[1].tostr(),
                                                                 self.param[2].tostr())
        elif self.op == "listgen":
            return " " * 4 * indent + "({} for {} in {})".format(self.param[0].tostr(0), self.param[1].tostr(),
                                                                 self.param[2].tostr())
        elif self.op == "attribute":
            return " " * 4 * indent + "{}.{}".format(self.param[0].tostr(0), self.param[1])
        elif self.op == "not":
            return " " * 4 * indent + "!{}".format(self.param[0].tostr(0))
        elif self.op == "indexing":
            return " " * 4 * indent + "{}[{}]".format(self.param[0].tostr(0), self.param[1].tostr(0))
        elif self.op in "=,+=,-=,*=,/=,+,-,*,/,>,<,>=,<,==,!=".split(","):
            return " " * 4 * indent + "{} {} {}".format(self.param[0].tostr(0), self.op, self.param[1].tostr(0))
        elif self.op == "define":
            return " " * 4 * indent + "var {} = {}".format(self.param[0].tostr(0), self.param[1].tostr(0))
        elif self.op == "return_V":
            return " " * 4 * indent + "return {}".format(self.param[0].tostr(0))
        elif self.op == "call":
            return " " * 4 * indent + "{}{}".format(self.param[0].tostr(0),
                                                    Value("tuple", self.param[1].param).tostr(0))
        elif self.op == "new":
            return " " * 4 * indent + "new {}{}".format(self.param[0].tostr(0),
                                                        Value("tuple", self.param[1].param).tostr(0))
        else:
            return " " * 4 * indent + (Value.op_name[self.op] if self.op in Value.op_name else self.op) + "({})".format(
                ",".join([x.tostr(0) if type(x) in [Value, Structure] else str(x) for x in self.param]))

    def get_listcomp(self, parent, code):
        _ret = []
        for i, pr in enumerate(self.param):
            if type(pr) == Value:
                if pr.op == "listcomp":
                    _ret.append((pr, code.temp_var))
                    self.param[i] = Value(
                        "var", ["_listcomp_" + str(code.temp_var)])
                    code.temp_var += 1
                else:
                    _ret += pr.get_listcomp(parent, code)
        return _ret

    def ispyformat(self, _str):
        _format = _str.split()
        if self.op != _format[1]:
            return False
        if type(self.param[0]) is Value and type(self.param[1]) is Value:
            return self.param[0].op == _format[0] and self.param[1].op == _format[2]
        else:
            return False

    def tojs(self, parent, code):
        self.param = [x.tojs(parent, code)[0] if type(
            x) is Value else x for x in self.param]
        if self.op == "var":
            if self.param[0] == "False":
                self.param[0] = "false"
            if self.param[0] == "True":
                self.param[0] = "true"
        if self.ispyformat("list * number"):
            if len(self.param[0].param) == 1:
                return [Value("call", [Value("attribute", [Value("new", [Value("var", ["Array"]), Value("list", [Value("number", [self.param[1].param[0]])])]), "fill"]), Value("list", [self.param[0].param[0]])])]
        if self.op == "call" and self.param[0].op == "attribute" and type(self.param[0].param[1]) is str:
            if self.param[0].param[1] == "append":
                self.param[0].param[1] = "push"
        if self.op == "call" and self.param[0].op == "var":
            if self.param[0].param[0] == "print":
                self.param[0] = Value(
                    "attribute", [Value("var", ["console"]), "log"])
            elif self.param[0].param[0] in code.class_list:
                self.op = "new"
                return [self]
        if self.op == "global_V":
            if self.param[0].op == "var":
                parent.var_list.append(self.param[0].tostr(0))
            elif self.param[0].op in ["list", "tuple"]:
                for glob in self.param[0].param:
                    parent.var_list.append(glob.tostr(0))
            return []
        if self.op == "=":
            if self.param[0].op == "tuple":
                if self.param[1].op in ["tuple", "list"]:
                    if len(self.param[0].param) != len(self.param[1].param):
                        show_error("Not equal arguments")
                    return [Value("=", [self.param[0].param[x], self.param[1].param[x]]).tojs(parent, code)[0] for x in
                            range(len(self.param[0].param))]
                else:
                    _ret = []
                    _ret.append(
                        Value("=", [Value("var", ["_tupassgn_{}".format(code.temp_var)]), self.param[1]]).tojs(parent,
                                                                                                               code)[0])
                    for lhi, lh in enumerate(self.param[0].param):
                        _ret.append(Value("=", [lh, Value("indexing", [
                            Value(
                                "var", ["_tupassgn_{}".format(code.temp_var)]),
                            Value("number", [str(lhi)])])]).tojs(parent, code)[0])
                    code.temp_var += 1
                    return _ret
            else:
                if self.param[0].op == "attribute" and self.param[0].param[0].tostr(0) == "self":
                    self.param[0].param[0].param[0] = "this"
                    return [self]
                if self.param[0].tostr(0) in parent.var_list:
                    return [self]
                else:
                    self.op = "define"
                    parent.var_list.append(self.param[0].tostr(0))
                    return [self]
        return [self]


class Structure:
    def __init__(self, struct, param):
        self.structure = struct
        self.param = param
        self.line = []

    def tostr(self, indent):
        _ret = ""
        _str = " " * 4 * indent
        i = 0
        structure = self.structure

        preassign = False

        if structure == "for A in V :" and type(self.param[1]) is Value and self.param[1].op == "call" and self.param[1].param[0].tostr(0) == "range":
            if len(self.param[1].param[1].param) == 1:
                preassign = True
                _str += ("for (var A=0; A < " + self.param[1].param[1].tostr(0)[
                         1:-1] + "; A++){").replace("A", self.param[0].tostr(0)[1:-1])
                         
        elif structure == "for A in V :":
            preassign = True
            print(self.param[0].tostr(0))
            _str += ("for (var A_index=0; A_index < " + self.param[1].tostr(0) + ".length" + "; A_index++){").replace("A", self.param[0].tostr(0)[1:-1])

        if structure == "if W :":
            structure = "if ( W ) {"
        if structure == "elif W :":
            structure = "else if ( W ) {"
        if structure == "else :":
            structure = "else {"
        if structure == "while W :":
            structure = "while ( W ) {"
        if structure == "def S L :":
            structure = "function S {"
        if structure == "class S L :":
            structure = "class S {"
        if structure == "class S :":
            structure = "class S {"
            self.param.append(Value("tuple", []))

        if not preassign:
            for strct in structure.split(" "):
                if strct == "S":
                    _str += self.param[i] + " "
                    i += 1
                elif strct in "VLW":
                    _str += self.param[i].tostr(0) + " "
                    i += 1
                elif strct in "A":
                    _str += self.param[i].tostr(0)[1:-1] + " "
                    i += 1
                else:
                    _str += strct + " "
        _ret += _str
        for ln in self.line:
            _ret += "\n" + ln.tostr(indent + 1) + \
                (";" if type(ln) is Value else "")
        _ret += "\n" + " " * 4 * indent + "}"
        return _ret

    def tojs(self, parent, code):
        if self.structure.split()[0] in "class,def".split(","):
            var_owner = self
            parent.var_list.append(self.param[0])
            if self.structure.split()[0] == "class":
                code.class_list.append(self.param[0])
            elif self.structure.split()[0] == "def" and parent.structure.split()[0] == "class":
                self.structure = "S L {"
                if self.param[0]=="__init__":
                    self.param[0]="constructor"
                self.param[1].param=self.param[1].param[1:]
        else:
            var_owner = parent
        if self.structure.split()[0] == "for":
            varname=self.param[0].tostr(0)[1:-1]
            self.line=[Value("define",[Value("var",[varname]),Value("var",[varname+"_index"])])]+self.line
        self.var_list = []
        _ret = []
        for i, l in enumerate(self.line):
            if type(l) == Value:
                lc = l.get_listcomp(var_owner, code)
                for _l in lc:
                    _t = _l[0]
                    _structure = Structure(
                        "for A in V :", [_t.param[1], _t.param[2]])
                    if len(_t.param) == 4:
                        _lcif = Structure("if V :", [_t.param[3]])
                        _lcif.line.append(
                            Value("call",
                                  [Value("attribute", [Value("var", ["_listcomp_{}".format(_l[1])]), "append"]),
                                   Value("list", [_t.param[0]])])
                        )
                        _lcif = _lcif.tojs(var_owner, code)[0]
                    else:
                        _structure.line += Value("call",
                                                 [Value("attribute",
                                                        [Value("var", ["_listcomp_{}".format(_l[1])]), "append"]),
                                                  Value("list", [_t.param[0]])]).tojs(var_owner, code)
                        _structure = _structure.tojs(var_owner, code)[0]
                    _ret += [
                        Value("=", [Value("var", ["_listcomp_" + str(_l[1])]), Value("list", [])]).tojs(var_owner,
                                                                                                        code)[0],
                        _structure
                    ]
            _ret += l.tojs(var_owner, code)
        self.line = _ret
        return [self]


def isletter(_str):
    if _str[0] not in char_list:
        return False
    for _s in _str:
        if not (_s in char_list or _s.isdigit()):
            return False
    return True


def parse_string(ind):
    bschar_list = {"n": "\n", "t": "\t", "\\": "\\", "\'": "\'", "\"": "\""}

    def check_str(_ind, l):
        return (len(code_str) >= _ind + l) and code_str[_ind:_ind + l]
    i = ind
    _ret = ""
    if ind >= len(code_str):
        return "\n", ind
    if code_str[i] in char_list:
        if check_str(i, 6) in ["not in", "is not"]:
            _ret = code_str[i:i + 6]
            i += 6
        else:
            while i < len(code_str) and ((code_str[i] in char_list) or code_str[i].isdigit()):
                _ret += code_str[i]
                i += 1
    elif code_str[i].isdigit():
        while i < len(code_str) and code_str[i].isdigit():
            _ret += code_str[i]
            i += 1
    elif code_str[i] in "\"\'":
        mline = False
        quote = code_str[i]
        if check_str(i, 3) == quote * 3:
            mline = True
            i += 3
        else:
            i += 1
        strdata = quote
        while i < len(code_str):
            if (not mline) and code_str[i] == quote:
                strdata += quote
                i += 1
                break
            elif mline and check_str(i, 3) == quote * 3:
                strdata += code_str[i]
                i += 3
                break
            elif code_str[i] == "\n":
                if mline:
                    strdata += code_str[i]
                    i += 1
                    continue
                else:
                    show_error("Unexpected end of string")
            elif code_str[i] == "\\":
                if len(code_str) <= i + 1:
                    show_error("Unexpected end of string")
                if check_str(i + 1, 1) in bschar_list:
                    strdata += bschar_list[code_str[i + 1]]
                else:
                    strdata += code_str[i:i + 2]
                i += 2
                continue
            else:
                strdata += code_str[i]
                i += 1
        _ret = strdata
    elif code_str[i] == " ":
        if i == 0:
            show_error("Misused indent")
        if code_str[i - 1] == "\n":
            while code_str[i] == " ":
                i += 1
                _ret += " "
        else:
            while code_str[i] == " ":
                i += 1
            return parse_string(i)
    else:
        multiple_symbol_list = ["==", "+=", "-=", "/=",
                                "*=", "!=", ">=", "<=", "**", "//", ">>", "<<"]
        for msl in multiple_symbol_list:
            if check_str(i, len(msl)) == msl:
                _ret = msl
                i += len(msl)
                break
        if _ret == "":
            _ret = code_str[i]
            i += 1
    return _ret, i


def parse_statement(ind, indent):
    statement_list = ["if", "elif", "else", "for", "while",
                      "def", "class", "with", "try", "except", "finally"]
    i = ind

    while i < len(code_str):
        while i < len(code_str):
            if code_str[i] == "\n":
                i += 1
                continue
            elif code_str[i] == " ":
                ii = i
                while ii < len(code_str) and code_str[ii] == " ":
                    ii += 1
                if ii < len(code_str) and code_str[ii] == "\n":
                    i = ii
                    continue
                else:
                    break
            else:
                break
        if i >= len(code_str):
            break
        if code_str[i] == " ":
            pw, ii = parse_string(i)
            if len(pw) > (indent + 1) * 4:
                show_error("Unexpected Indent")
            elif len(pw) < (indent + 1) * 4:
                break
            i = ii
        else:
            break

    t, _ = parse_string(i)
    for sl in statement_list:
        if t == sl:
            return parse_structure(i, indent)
    ps, i = parse_line(i)
    if i >= len(code_str):
        return ps, i
    while code_str[i] == " ":
        i += 1
    if code_str[i] != "\n":
        if code_str[i] == "#":
            while i < len(code_str) and code_str[i] != "\n":
                i += 1
            return ps, i
    return ps, i


def parse_format(ind, _structure):
    i = ind
    param = []
    for st in _structure:
        while i < len(code_str) and code_str[i] in " \n":
            i += 1
        if st == "S":
            t, i = parse_string(i)
            if isletter(t):
                param.append(t)
                continue
            else:
                return False, ind
        elif st == "V":
            t, i = parse_value(i, False)
            if t is False:
                return False, ind
            param.append(t)
            continue
        elif st == "A":
            _ret = []
            t, i = parse_var(i)
            if t is False:
                return False, ind
            _ret.append(t[0])
            while parse_string(i)[0] == ",":
                i = parse_string(i)[1]
                if parse_var(i)[0]:
                    _ret.append(parse_var(i)[0][0])
                    i = parse_var(i)[1]
                    continue
                return False, ind

            param.append(Value("list", _ret))
            continue
        elif st == "W":
            t, i = parse_value_without_baretuple(i)
            if not t:
                return False, ind
            param.append(t)
            continue
        elif st == "L":
            t, i = parse_value_without_baretuple(i)
            if (not t) or (t.op != "tuple"):
                return False, ind
            param.append(t)
            continue
        else:
            t, i = parse_string(i)
            if t != st:
                return False, ind
            continue
    return param, i


def parse_structure(ind, indent):
    structure_list = [
        "if W :".split(),
        "elif W :".split(),
        "else :".split(),
        "for A in V :".split(),
        "while W :".split(),
        "def S L :".split(),
        "class S L :".split(),
        "class S :".split(),
        "with V as A :".split(),
        "try :".split(),
        "except S as W :".split(),
        "except S :".split(),
        "except :".split(),
        "finally :".split()
    ]
    lines = []
    for st_l in structure_list:
        i = ind
        pf, i = parse_format(i, st_l)
        if pf is False:
            continue
        _ret = Structure(" ".join(st_l), pf)

        while code_str[i] == " ":
            i += 1
        if code_str[i] == "#":
            while i < len(code_str) and code_str[i] != "\n":
                i += 1
        if i < len(code_str) and not code_str[i] == "\n":
            pv, i = parse_line(i)
            if not pv:
                show_error("Invalid Syntax")
            while code_str[i] == " ":
                i += 1
            if code_str[i] == "#":
                while i < len(code_str) and code_str[i] != "\n":
                    i += 1
            if code_str[i] != "\n":
                show_error("Invalid Syntax")
            i += 1
            lines.append(pv)
        while i < len(code_str):
            while i < len(code_str):
                if code_str[i] == "\n":
                    i += 1
                    continue
                elif code_str[i] == " ":
                    ii = i
                    while code_str[ii] == " ":
                        ii += 1
                    if code_str[ii] == "\n":
                        i = ii
                        continue
                    else:
                        break
                elif code_str[i] == "#":
                    while i < len(code_str) and code_str[i] != "\n":
                        i += 1
                    continue
                else:
                    break
            if i >= len(code_str):
                break
            if code_str[i] == " ":
                pw, ii = parse_string(i)
                if len(pw) > (indent + 1) * 4:
                    show_error("Unexpected Indent")
                elif len(pw) < (indent + 1) * 4:
                    break
                i = ii
            else:
                break
            p_st, i = parse_statement(i, indent + 1)
            if p_st:
                lines.append(p_st)
            else:
                break
        _ret.line = lines
        return _ret, i
    show_error("Misused Statement")


def parse_var(ind):
    i = ind

    def find_word(ind):
        def search_not(_ind):
            ps, ii = parse_string(_ind)
            if ps == "not":
                return "not", ii
            return False, _ind

        def search_neg(_ind):
            ps, ii = parse_string(_ind)
            if ps == "-":
                return "-", ii
            return False, _ind

        def search_letter(_ind):
            ps, ii = parse_string(_ind)
            if isletter(ps):
                return Value("var", [ps]), ii
            else:
                return False, _ind

        def search_listcomp_if(_ind):
            pf, ii = parse_format(_ind, "[ W for A in V if V ]".split())
            if pf is False:
                return False, _ind
            return Value("listcomp", pf), ii

        def search_listcomp(_ind):
            pf, ii = parse_format(_ind, "[ W for A in V ]".split())
            if pf is False:
                return False, _ind
            return Value("listcomp", pf), ii

        def search_list(_ind):
            pf, i = parse_string(_ind)
            if pf != "[":
                return False, _ind
            listdata = []
            while i < len(code_str):
                while code_str[i] in " \n":
                    i += 1
                pf, ii = parse_string(i)
                if pf == "]":
                    return Value("list", listdata), ii
                while code_str[i] in " \n":
                    i += 1
                pf, i = parse_value_without_baretuple(i)
                if not pf:
                    return False, _ind
                listdata.append(pf)
                while code_str[i] in " \n":
                    i += 1
                pf, i = parse_string(i)
                if pf == ",":
                    continue
                elif pf == "]":
                    return Value("list", listdata), i
                else:
                    return False, _ind
            show_error("Unexpected End in parsing list")

        def search_dict(_ind):
            pf, i = parse_string(_ind)
            if pf != "{":
                return False, _ind
            listdata = []
            while i < len(code_str):
                while code_str[i] in " \n":
                    i += 1
                pf, ii = parse_string(i)
                if pf == "}":
                    return Value("dictionary", listdata), ii
                while code_str[i] in " \n":
                    i += 1
                pf, ii = parse_format(i, "W : W".split())
                if pf is False:
                    return False, _ind
                i = ii
                listdata.append(Value("tuple", pf))
                while code_str[i] in " \n":
                    i += 1
                pf, i = parse_string(i)
                if pf == ",":
                    continue
                elif pf == "}":
                    return Value("dictionary", listdata), i
                else:
                    return False, _ind
            show_error("Unexpected End in parsing list")

        def search_listgen(_ind):
            pf, ii = parse_format(_ind, "( W for A in V )".split())
            if pf is False:
                return False, _ind
            return Value("listgen", pf), ii

        def search_tuple(_ind):
            pf, i = parse_string(_ind)
            if pf != "(":
                return False, _ind
            listdata = []
            while i < len(code_str):
                while code_str[i] in " \n":
                    i += 1
                pf, ii = parse_string(i)
                if pf == ")":
                    return Value("tuple", listdata), ii
                while code_str[i] in " \n":
                    i += 1
                pf, i = parse_value_without_baretuple(i)
                if pf is False:
                    return False, _ind
                listdata.append(pf)
                while code_str[i] in " \n":
                    i += 1
                pf, i = parse_string(i)
                if pf == ",":
                    continue
                elif pf == ")":
                    return Value("tuple", listdata), i
                else:
                    return False, _ind
            return False, _ind

        def search_string(_ind):
            pw, ii = parse_string(_ind)
            if pw[0] in "\"\'":
                return Value("string", [pw]), ii
            return False, _ind

        def search_number(_ind):
            ps, i = parse_string(_ind)
            if ps.isdigit():
                pps, ii = parse_string(i)
                if pps == ".":
                    ppps, iii = parse_string(ii)
                    if ppps.isdigit():
                        return Value("number", [ps + "." + ppps]), iii
                    else:
                        return Value("number", [ps + ".0"]), ii
                else:
                    return Value("number", [ps]), i
            elif ps == ".":
                pps, ii = parse_string(i)
                if pps.isdigit():
                    return Value("number", ["0." + pps]), ii
                else:
                    return False, _ind
            elif ps == "-":
                if code_str[i] == "-":
                    return False, _ind
                sn = search_number(i)
                if sn[0]:
                    return Value("number", ["-" + sn[0].param[0]]), sn[1]
                else:
                    return False, _ind
            return False, _ind
        checklist = [search_not, search_number, search_neg, search_letter, search_listcomp_if, search_listcomp,
                     search_list, search_listgen, search_tuple,
                     search_dict, search_string]
        for cl in checklist:
            search, i = cl(ind)
            if search:
                return search, i
        return False, ind

    def find_attach(ind):
        def search_indexing(_ind):
            pf, i = parse_format(_ind, "[ W ]".split())
            if pf is False:
                return False, _ind
            return Value("indexing", [pf[0]]), i

        def search_slicing(_ind):
            pf, i = parse_format(_ind, "[ : ]".split())
            if pf is not False:
                return Value("slicing", [None, None]), i
            pf, i = parse_format(_ind, "[ W : ]".split())
            if pf is not False:
                return Value("slicing", [pf[0], None]), i
            pf, i = parse_format(_ind, "[ : W ]".split())
            if pf is not False:
                return Value("slicing", [None, pf[0]]), i
            pf, i = parse_format(_ind, "[ W : W ]".split())
            if pf is not False:
                return Value("slicing", pf), i
            return False, _ind

        def search_calling(_ind):
            def get_arguments(__ind):
                pf, i = parse_string(__ind)
                if pf != "(":
                    return False, __ind
                listdata = []
                while i < len(code_str):
                    while code_str[i] in " \n":
                        i += 1
                    pf, ii = parse_string(i)
                    if pf == ")":
                        return listdata, ii
                    pf, i = parse_value_without_baretuple(i)
                    if not pf:
                        return False, __ind
                    listdata.append(pf)
                    while code_str[i] in " \n":
                        i += 1
                    pf, i = parse_string(i)
                    if pf == ",":
                        continue
                    elif pf == ")":
                        return listdata, i
                    else:
                        show_error("Invalid syntax parsing tuple", _ind)
                show_error("Unexpected End in parsing tuple", _ind)
            ga, ii = get_arguments(_ind)
            if ga is not False:
                return Value("call", [Value("list", ga)]), ii
            return False, _ind
        checklist = [search_indexing, search_slicing, search_calling]
        for cl in checklist:
            search, i = cl(ind)
            if search:
                return search, i
        return False, ind

    def find_dot(ind):
        _ret = []
        i = ind
        while True:
            pf, ii = parse_format(i, ". S".split())
            if pf is False:
                break
            i = ii
            _ret.append(pf[0])
        return _ret, i
    _ret = []
    while i < len(code_str):
        fw, i = find_word(i)
        if fw == "not":
            _ret.append("not")
            continue
        elif fw == "-":
            _ret.append("__neg__")
            continue
        elif fw is False:
            return False, ind
        else:
            _ret.append(fw)
            break
    while i < len(code_str):
        fa, ii = find_attach(i)
        if fa:
            fa.param = [_ret[-1]] + fa.param
            _ret[-1] = fa
            i = ii
            continue
        ps, _ = parse_string(i)
        if ps == ".":
            fd, i = find_dot(i)
            for _fd in fd:
                _ret[-1] = Value("attribute", [_ret[-1], _fd])
            continue
        break
    while "__neg__" in _ret:
        ii = _ret.index("__neg__")
        if ii == len(_ret) - 1:
            show_error("Error parsing operators")
        _ret[ii:ii + 2] = [Value(_ret[ii], [_ret[ii + 1]])]
    while "__pos__" in _ret:
        ii = _ret.index("__pos__")
        if ii == len(_ret) - 1:
            show_error("Error parsing operators")
        _ret[ii:ii + 2] = [_ret[ii + 1]]
    return _ret, i


def parse_value(ind, doassign=True):
    pv, i = parse_value_without_baretuple(ind, doassign)
    if not pv:
        return False, ind
    ps, ii = parse_string(i)
    if ps == ",":
        i = ii
        tupledata = [pv]
        while i < len(code_str):
            while code_str[i] == " ":
                i += 1
            pv, i = parse_value_without_baretuple(i, doassign)
            if not pv:
                break
            tupledata.append(pv)
            if i >= len(code_str):
                break
            while code_str[i] == " ":
                i += 1
            pv, ii = parse_string(i)
            if pv == ",":
                i = ii
                continue
            break
        return Value("tuple", tupledata), i
    else:
        return pv, i


def parse_value_without_baretuple(ind, doassign=True):
    def find_statement(ind):
        keyword_list = [
            "break".split(),
            "continue".split(),
            "from V import * as A".split(),
            "from V import V as A".split(),
            "from V import *".split(),
            "from V import V".split(),
            "import V as A".split(),
            "import V".split(),
            "pass".split(),
            "return V".split(),
            "raise V".split(),
            "raise".split(),
            "yield V".split(),
            "yield".split(),
            "lambda V : V".split(),
            "global V".split(),
        ]
        for kl in keyword_list:
            pf, i = parse_format(ind, kl)
            if pf is False:
                continue
            return Value("_".join(kl), pf), i
        return False, ind

    def find_operation(ind):
        operator_list = ((
            "=,+=,-=,*=,/=,if,else," if doassign else "") + "==,!=,<=,>=,is,is not,in,not in,+,-,*,/,>,<,|,**,//,>>,<<,and,or,%,^,&").split(
            ",")
        ps, i = parse_string(ind)
        if ps not in operator_list:
            return False, ind
        return ps, i

    def bind(_list):
        p_list = _list
        operator_list = [t.split(",") for t in
                         ("**.*,/,%,//.+,-.>>,<<.&.^.|.<=,>=,>,<,!=,==,is,is not,in,not in.not.and.or.if_else" + (
                             ".=,+=,-=,*=,/=" if doassign else "")).split(
                             ".")]
        for e_operator in operator_list:
            if e_operator == ["not"]:
                while "not" in p_list:
                    i = p_list.index("not")
                    if i == len(p_list) - 1:
                        show_error("Error parsing operators")
                    p_list[i:i + 2] = [Value("not", [p_list[i + 1]])]
            if e_operator == ["if_else"]:
                while "if" in p_list and "else" in p_list:
                    i1 = p_list.index("if")
                    i2 = p_list.index("else")
                    if i1 == 0 or i2 != i1 + 2 or i2 >= len(p_list):
                        show_error("Error parsing operators _if_else_")
                    p_list[i1 - 1:i2 + 2] = [
                        Value("ternary", [p_list[i1 - 1], p_list[i1 + 1], p_list[i2 + 1]])]
            while any([k in p_list for k in e_operator]):
                i = min(
                    [p_list.index(k) if k in p_list else 1000 for k in e_operator])
                if e_operator[0] == "**":
                    i = len(p_list) - 1 - list(reversed(p_list)).index("**")
                if not (i > 0 and i < len(p_list) - 1):
                    return False
                    # show_error("Error parsing operators")
                if not (type(p_list[i - 1]) is Value and type(p_list[i + 1]) is Value):
                    return False
                    # show_error("Error parsing operators")
                p_list[i - 1:i +
                       2] = [Value(p_list[i], [p_list[i - 1], p_list[i + 1]])]
        if len(p_list) != 1:
            return False
        return p_list[0]
    fs, ii = find_statement(ind)
    if fs:
        return fs, ii
    i = ind
    p_list = []
    while i < len(code_str):
        while code_str[i] == " ":
            i += 1
        fw, i = parse_var(i)
        if fw is False:
            return False, ind
        p_list += fw
        if i >= len(code_str):
            break
        fo, ii = find_operation(i)
        if fo:
            i = ii
            p_list.append(fo)
            continue
        break
    return bind(p_list), i


def parse_line(ind):
    pv, i = parse_value(ind, doassign=False)
    if parse_string(i)[0] in "=,+=,-=,*=,/=".split(","):
        ii = parse_string(i)[1]
        return Value(parse_string(i)[0], [pv, parse_value(ii)[0]]), parse_value(ii)[1]
    if parse_string(i)[0] == "\n":
        return pv, i
    if parse_string(i)[0] == "#":
        i = parse_string(i)[1]
        while i < len(code_str) and code_str[i] != "\n":
            i += 1
        return pv, i
    return False, ind


def parse_code():
    main = Code("main")
    i = 0
    while i < len(code_str):
        while i < len(code_str):
            pv, ii = parse_string(i)
            if pv == "#":
                while i < len(code_str) and code_str[i] != "\n":
                    i += 1
            if pv == "\n":
                i = ii
            else:
                break
        ps, i = parse_statement(i, 0)
        if ps is False:
            k = ""
            while i < len(code_str) and code_str[i] != "\n":
                k += code_str[i]
                i += 1
            if i == len(code_str):
                break
            show_error("wrong code at: \"{}\"".format(k), i)
            break
        main.line.append(ps)
    return main


if __name__ == '__main__':
    filename = "code.py"
    with open(filename, "r") as f:
        code_str = f.read()
    pc = parse_code()
    pc.tojs()
    with open("result.js", "w") as f:
        f.write(pc.tostr())
