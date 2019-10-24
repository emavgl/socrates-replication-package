From Kore Analysis we have a folder with the following directory tree:

```
testfull10
    0/
        /output
        /configuration
    1/
        /output
        /configuration
...
```

There are two utility to analyze the scripts:

### print_cluster_logs.py

Create a CSV summarizing the violations.

Each row is a tested contract address;
Columns are the number of violations for I1, I2, I6, I7, I8, I9.

```
python3 cluster_logs.py <test-folder> <experiment_input_folder> <number-of-runs>
```

es.

```
python3 cluster_logs.py testfull10 input_1000_contracts 10
```

Results:

```
0x922105fad8153f516bcfb829f56dc097a0e1d705,YEEToken,0,0,0,0,0,0
0x960f56e8a9f2084acf39a686ee5b1f5467cf81e4,ZBAStandardToken,0,0,0,0,0,0
0x351d5ea36941861d0c03fdfb24a8c2cb106e068b,FrescoToken,0,0,0,0,0,0
0xaa843f65872a25d6e9552ea0b360fb1d5e333124,EcoValueCoin,0,0,0,0,0,0
0x0d8775f648430679a709e98d2b0cb6250d2887ef,BAToken,0,0,0,0,0,0
0x69beab403438253f13b6e92db91f7fb849258263,NeuroToken,0,0,0,0,0,0
0xfa05a73ffe78ef8f1a739473e462c54bae6567d9,LunyrToken,0,0,0,0,0,0
0xb2f7eb1f2c37645be61d73953035360e768d81e6,CobinhoodToken,1,5,0,0,0,0
0xcfc2437916a6df165235272dbfb116687bb1a00b,PlusCoin,0,0,0,0,0,0
0x4fe9f52ec23f6805f2fd0332a34da4f1c135b024,CaiToken,0,0,0,0,0,0
```


### find.py

From the CSV we know that `CobinhoodToken` has 5 violations of `I2` and 1 of `I1`.
But what if I want to do manual analysis? Where can I find the log that lead to the violations?

```
cd testfull10
python3 find.py <contract-address> <invariants1>-<invariant2>
```

es.

```
cd testfull10
python3 find.py 0xb2f7eb1f2c37645be61d73953035360e768d81e6 I1-I2
```

will search for a test where both invariant `I1` and `I2` have been violated.



