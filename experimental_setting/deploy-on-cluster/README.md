# Experiment description

- testfull10: all behaviours, 10 bots
- testfull1: all behaviours, 1 bots
- testoverflow10: overflow behaviour, 10 bots
- testboundary10: boundary, 10 bots
- testrandom10: random, 10 bots
- testcombinedrandom10: boundary + random, 10 bots

# Utils

- `run-script.sh <input-folder>`: qsub of all the .sh script in an input folder
- `replicate.py <template-input-script> <output-folder> <times>`: creates `times` times scripts from the template script
- `copy-folder-n-times.bash <input-folder> <ouput-folder> <times>`: creates `n` copies of `input-folder` in `outputfolder` as `0, 1, 2, 3...n`
- `print_cluster_logs.py <input-folder>`: collect the results and build a csv with the results in `input-folder`.

# How to deploy

## 1. Copy test folder and test-submit-script

Copy `testfull10` and `testfull10.sh` in the login cluster.

- `testfull10` folder contains `input`, empty `output` and `testconf` with test configuration
- `testfull10.sh` is a template used to run `testfull10` experiments

## 2. Replicate

Since we want to run it 10 times. We need to replicate the script using

```bash
python3 replicate.py testfull10.sh testfull10-run-scripts 10
```

and

```bash
bash copy-folder-n-times.sh testfull10 experiments/testfull10 10
```

to replicate the folder testfull10 in experiments/testfull10  
the result will be:

```
experiments/testfull10/0
experiments/testfull10/1
experiments/testfull10/2
...
```

## 3. Submit jobs

At this point, you are ready to submit the jobs

Use the script

```
bash run-script.sh testfull10-run-scripts
```

random ok
combinedrandom ok
testfull10 ok
testfull1 ok
testboundary ok
overflow ok
