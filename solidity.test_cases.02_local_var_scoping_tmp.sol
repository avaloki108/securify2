
pragma solidity ^0.5.0;

contract A {
    function test1() public payable {
        uint a = 4; // a
        uint b = 5; // a, b

        { // a, b
            uint q = 4; // a, b, q
            b+=1; // a, b, q
        }

        b+=1; // a, b

        if (true)
        { // a, b
            uint e; // a, b, e
        }
        else
        {
            uint f; // a, b, f
            f+=1; // a, b, f
            uint g; // a, b, f, g
        }

        for ( // a, b
            uint i = 10; // a, b, i
            i < 100;
            ++i)
        {
        }
    }

    function test2(uint arg) public payable {
        if (true) // arg
        { // arg
            uint e; // arg, e
        }
    }

    function test3(uint arg) public returns(uint ret) {
        ret = arg; // ret, arg
    }
}

