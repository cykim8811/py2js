class World:
    def __init__(self):
        self.primary = []
        self.propositions = []

    def all_posp(self):
        return list(range(2 ** len(self.primary)))

    def isValid(self, premise, conclusion):
        _tot = Proposition(self, self.all_posp())
        for pr in premise:
            _tot = _tot * pr

        return (_tot > conclusion).isTautology()


class Proposition:
    def __init__(self, world, arg):  # arg(str): new primary prop; arg(list): new prop with data arg;
        self.world = world
        if type(arg) is str:
            for opr in self.world.propositions:
                opr.table = opr.table + [opt + 2 ** len(self.world.primary) for opt in opr.table]
            self.world.primary.append(arg)
            self.table = [2 ** (len(self.world.primary) - 1) + k for k in range(2 ** (len(self.world.primary) - 1))]
            self.world.propositions.append(self)
        else:
            self.table = arg
            self.world.propositions.append(self)

    def get_posp(self):
        return self.world.all_posp()

    def __mul__(self, other):
        return self & other

    def __and__(self, other):
        return Proposition(self.world,[x for x in self.get_posp() if ((x in self.table) and (x in other.table))])

    def __add__(self, other):
        return self | other

    def __or__(self, other):
        return Proposition(self.world, [x for x in self.get_posp() if (x in self.table) or (x in other.table)])

    def __repr__(self):
        return "<{}>".format(",".join(["".join(["1" if (psp & 2 ** i) else "0" for i in range(len(self.world.primary))]) for psp in self.table]))

    def __neg__(self):
        return Proposition(self.world, [x for x in self.get_posp() if (x not in self.table)])

    def __gt__(self, other):
        return -self | other

    def __eq__(self, other):
        return (self > other) & (other > self)

    def isTautology(self):
        return all([x in self.table for x in self.get_posp()])
