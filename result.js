var a = 0;
var b = [];
var c = "hello world";
var d = 1;
var e = 2;
var f = 3;
e = f;
f = e;
var _tupassgn_0 = range(3);
e = _tupassgn_0[0];
var h = _tupassgn_0[1];
var i = _tupassgn_0[2];
var temp = "whatever";
function say (string) { 
    var temp = "I say ";
    console.log(temp + string);
}
function hear () { 
    temp = "this";
    console.log(temp);
}
var _listcomp_1 = [];
for (var x=0; x < 100; x++){
    _listcomp_1.push(x * 2 - 1);
}
var l = _listcomp_1;
var _listcomp_2 = [];
for (var y=0; y < 10; y++){
    var _listcomp_3 = [];
    for (var x=0; x < y; x++){
        _listcomp_3.push(x);
    }
    _listcomp_2.push(_listcomp_3);
}
var muldim = _listcomp_2;