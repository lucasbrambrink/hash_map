#Hashmap

Implements a hashmap with amortized constant lookup in Python. Using open addressing
and
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
```

#Reconciliation

```
cd reconciliation
python3 -m unittest tests.py
python3 reconciliation.py recon.in
cat recon.out
```