# data-mining-pmi

Use point-wise-information(PMI) to mine hot candidates.

# file lists:

+ *data\_preparation.py*: generate n-gram words collection to build trie, and also candidate
+ *data\_process.py*: use n-gram to build trie and calculate PMI
+ pygtrie: google's python trie implementation. (Better use pip to install it.)

# Reference

+ [知乎悟空](https://zhuanlan.zhihu.com/p/25499358?columnSlug=f4239f530c65ad0d3218bf51735cb5be)
+ [Trie](https://github.com/google/pygtrie)
