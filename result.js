
class World { 
    constructor () { 
        this.primary = [];
        this.propositions = [];
    }
    all_posp () { 
        return list(range(pow(2,len(self.primary))));
    }
    isValid (premise,conclusion) { 
        var _tot = Proposition(self,self.all_posp());
        for (var pr_index=0; pr_index < premise.length; pr_index++){
            var pr = pr_index;
            _tot = _tot * pr;
        }
        return (_tot > conclusion).isTautology();
    }
}
class Proposition { 
    constructor (world,arg) { 
        this.world = world;
        if ( is(type(arg),str) ) { 
            for (var opr_index=0; opr_index < self.world.propositions.length; opr_index++){
                var opr = opr_index;
                var _listcomp_0 = [];
                for (var opt_index=0; opt_index < opr.table.length; opt_index++){
                    var opt = opt_index;
                    _listcomp_0.push(opt + pow(2,len(self.world.primary)));
                }
                var opr.table = opr.table + _listcomp_0;
            }
            self.world.primary.push(arg);
            var _listcomp_1 = [];
            for (var k=0; k < pow(2,(len(self.world.primary) - 1)); k++){
                var k = k_index;
                _listcomp_1.push(pow(2,(len(self.world.primary) - 1)) + k);
            }
            this.table = _listcomp_1;
            self.world.propositions.push(self);
        }
        else { 
            this.table = arg;
            self.world.propositions.push(self);
        }
    }
    get_posp () { 
        return self.world.all_posp();
    }
    __mul__ (other) { 
        return andb(self,other);
    }
    __and__ (other) { 
        var _listcomp_2 = [];
        for (var x_index=0; x_index < self.get_posp().length; x_index++){
        }
        return new Proposition(self.world,_listcomp_2);
    }
    __add__ (other) { 
        return orb(self,other);
    }
    __or__ (other) { 
        var _listcomp_3 = [];
        for (var x_index=0; x_index < self.get_posp().length; x_index++){
        }
        return new Proposition(self.world,_listcomp_3);
    }
    __repr__ () { 
        var _listcomp_4 = [];
        for (var psp_index=0; psp_index < self.table.length; psp_index++){
            var psp = psp_index;
            var _listcomp_5 = [];
            for (var i=0; i < len(self.world.primary); i++){
                var i = i_index;
                _listcomp_5.push(ternary("1",(andb(psp,pow(2,i))),"0"));
            }
            _listcomp_4.push("".join(_listcomp_5));
        }
        return "<{}>".format(",".join(_listcomp_4));
    }
    __neg__ () { 
        var _listcomp_6 = [];
        for (var x_index=0; x_index < self.get_posp().length; x_index++){
        }
        return new Proposition(self.world,_listcomp_6);
    }
    __gt__ (other) { 
        return orb(__neg__(self),other);
    }
    __eq__ (other) { 
        return andb((self > other),(other > self));
    }
    isTautology () { 
        var _listcomp_7 = [];
        for (var x_index=0; x_index < self.get_posp().length; x_index++){
            var x = x_index;
            _listcomp_7.push(in(x,self.table));
        }
        return all(_listcomp_7);
    }
}