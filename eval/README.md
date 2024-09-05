# Eval setup

## Running the eval
`eval.py` is the driver script, inside eval dir do the following:
```sh
python .\eval.py --input-dir dataset --output-dir result 
```
For each file in dataset, the results are generated in dir result.

## Understanding the result
The result dir will have multiple top-level csv files with all the results.
* `num-grounded-rules.csv`: how many of the total rules are grounded (total, grounded)
* `num-valid-tests.csv`: how many of the generated test cases follow the input spec (total, valid)
* `num-failing-tests.csv`: how many of the test cases failed (total, failed) 
* `num-valid-failing-tests.csv`: how many of the valid test cases failed (valid, failed)
* `num-failing-tests-with-rules.csv`: to check coverage we make a prompt using the intent and the rules, how many test cases does that prompt fails (total, failed)
* `num-baseline-valid-tests.csv`: how many of the baseline generated test cases follow the input spec (total, valid)
* `num-baseline-failing-tests.csv`: how many of the baseline test cases failed (total, failed) 
* `num-baseline-valid-failing-tests.csv`: how many of the baseline valid test cases failed (valid, failed)
