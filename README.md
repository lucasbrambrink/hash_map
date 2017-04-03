# YChars Coding Project

I decided to have a little fun this weekend and took a shot at both question 1. and 3. Unzip the
compressed file and ```cd``` into either ```hash_map``` or ```reconciliation``` directories to interact with the programs.
Both are written in Python 3, and have a rich testing environment that can be run via 
```python3 -m unittest tests.py```


## Hashmap

Implements a hashmap with amortized constant lookup in Python using open addressing
and serial probing. 

It currently has 2 separate hashing algorithms (base-N char->int conversion, or sha256)
where HASH mod SIZE provides ~uniform distribution between 0 - SIZE. The testing module 
exposes 2 tests to show reasonably uniform distribution. 

Implements built-in instance methods to for a rich object API. Behaves similar to Python dictionary.


```
cd hashmap
python3 -m unittest tests.py
python3
>>> from hash_map import HashMap
>>> hm = HashMap(foo='bar')
>>> hm
{"foo": bar}
>>> hm['test'] = 1
>>> hm['test']
1
>>> hm['foo']
'bar'
```

## Reconciliation

Reconciles the final reported positions with a given transaction history, and writes failures to disk.
In broad terms, it implements the following scheme:
1. initialize PortfolioA from D0 positions, and apply D1 transactions
2. initialize PortfolioB from D1 positions (reported)
3. take the difference of PorfolioB - PortfolioA, and identify failures (i.e. non-zero values). Ideally, there would be no difference between the two portfolios.

Script takes 2 command line arguments, input_path and (optional) output path, respectively. Can also be used as a module.
This module especially is written to be extensible, such that logging and/or other IO processes can be integrated easily. 

``` 
cd reconciliation
python3 -m unittest tests.py
python3 reconciliation.py recon.in
cat recon.out
```