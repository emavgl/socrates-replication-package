# Results

Results of Echidna on a random sample of contracts.  
Tested with Echidna (master version) on 18 Dec.
https://github.com/trailofbits/echidna/tree/d93c226b2ad4ff884f33faa850d7d36556c12211

| TokenName | Invariant | Result   |
|--------------|----|--------------|
| ExpressCoin  | I1 | VIOLATED     |
| AEToken      | I1 | VIOLATED     |
| DNCEQuity    | I1 | VIOLATED     |
| DELTAToken   | I2 | VIOLATED     |
| Yumerium     | I2 | NOT VIOLATED |
| Tube         | I2 | NOT VIOLATED |
| TCZToken     | I6 | NOT TESTABLE |
| JAAGCoin     | I6 | NOT VIOLATED |
| MKC          | I7 | NOT VIOLATED |
| CoinfairCoin | I8 | VIOLATED     |
| Bible        | I9 | VIOLATED     |

## I1 (3 samples)
- ExpressCoin: overflow con mint **VIOLATED**
- AEToken: overflow on transfer if prefill called with high values **VIOLATED**
- DNCEQuity: overflow **VIOLATED**

## I2 (3 samples)
- DELTAToken: fail at start, not all token distributed **VIOLATED**
- Yumerium: mintToken overflow **NOT VIOLATED**
- Tube: mintToken overflow **NOT VIOLATED**

## I6 (2 samples, 1 testable)
- TCZToken: trasferFrom without allowance, only by the owner **CANNOT WRITE INVARIANT**
- JAAGCoin: transferFrom doesn't check allowance ****

## I7 (1 sample)
- MKC: allowance after transferFrom not consistent due to implementation error **NOT VIOLATED**

## I8 (1 sample)
- CoinfairCoin: transfer between admin creates doesn't transfer tokens but create new ones, not consistent with logs. **VIOLATED**

## I9 (1 sample)
- Bible: no event Approval is emitted **VIOLATED**

## LATEX
```
\begin{table}[]
\begin{tabular}{|l|l|l|}
\hline
ExpressCoin  & I1 & VIOLATED     \\ \hline
AEToken      & I1 & VIOLATED     \\ \hline
DNCEQuity    & I1 & VIOLATED     \\ \hline
DELTAToken   & I2 & VIOLATED     \\ \hline
Yumerium     & I2 & NOT VIOLATED \\ \hline
Tube         & I2 & NOT VIOLATED \\ \hline
TCZToken     & I6 & NOT TESTABLE \\ \hline
JAAGCoin     & I6 & NOT VIOLATED \\ \hline
MKC          & I7 & NOT VIOLATED \\ \hline
CoinfairCoin & I8 & VIOLATED     \\ \hline
Bible        & I9 & VIOLATED     \\ \hline
\end{tabular}
\end{table}
```

# Config

```
#Arguments to solc
#solcArgs:

#Choose the number of epochs to use in coverage-guided testing
epochs: 2

#Set the gas limit for each test
gasLimit: "0xfffff"

#Number of tests that will run for each property
testLimit: 10000

#Max call sequence length
range: 100

#Contract's address in the EVM
contractAddr: "0x00a329c0648769a73afac7f9381e08fb43dbea72"

#Sender's address in the EVM
# sender == deployer
deployer: "0x00a329c0648769a73afac7f9381e08fb43dbea70"
sender: "0x00a329c0648769a73afac7f9381e08fb43dbea72"
#sender: ["0x00a329c0648769a73afac7f9381e08fb43dbea70", "0x0000000000000000000000000000000000000010", "0x0000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000002", "0x0000000000000000000000000000000000000004", "0x0000000000000000000000000000000000000005", "0x0000000000000000000000000000000000000006", "0x0000000000000000000000000000000000000007", "0x0000000000000000000000000000000000000008", "0x0000000000000000000000000000000000000009"]

#List of addresses that will be used in all tests
addrList: ["0x0000000000000000000000000000000000000010", "0x0000000000000000000000000000000000000001", "0x0000000000000000000000000000000000000002", "0x0000000000000000000000000000000000000004", "0x0000000000000000000000000000000000000005", "0x0000000000000000000000000000000000000006", "0x0000000000000000000000000000000000000007", "0x0000000000000000000000000000000000000008", "0x0000000000000000000000000000000000000009"]

#Shrink Limit
shrinkLimit: 100

#Test Prefix
prefix: "echidna_"

#Print full coverage
printCoverage: false
#Return Type
#  - Success: all tests should return true
#  - Fail: all tests should return false
#  - Throw: all tests should revert
#  - Fail or Throw: all tests should either return false or revert
returnType: "Success"


#Gas limit
#gasLimit

```


# Run on cluster

- Set max tests = 100000;
- Added a timeout of 5 minutes.

```
eviglianisi@korehpc083:~/echidna/echidna-inputs$ timeout 5m echidna-test MKC.sol MKC --config="config.yaml"
━━━ MKC.sol ━━━
  ● "echidna_invariant_I7" passed 19391 tests (running)
  ○ 0/1 complete (running)

eviglianisi@korehpc083:~/echidna/echidna-inputs$ timeout 5m echidna-test JAAGCoin.sol JAAGCoin --config="config.yaml"
━━━ JAAGCoin.sol ━━━
  ● "echidna_invariant_I6" passed 18246 tests (running)
  ○ 0/1 complete (running)

eviglianisi@korehpc083:~/echidna/echidna-inputs$ timeout 5m echidna-test Tube.sol Tube --config="config.yaml"
"Analyzing contract: Tube.sol:Tube"
━━━ Tube.sol ━━━
  ● "echidna_invariant_I2" passed 5792 tests (running)
  ○ 0/1 complete (running)

eviglianisi@korehpc083:~/echidna/echidna-inputs$ timeout 5m echidna-test Yumerium.sol Yumerium --config="config.yaml"
"Analyzing contract: Yumerium.sol:Yumerium"
━━━ Yumerium.sol ━━━
  ● "echidna_invariant_I2" passed 5820 tests (running)
  ○ 0/1 complete (running)
```