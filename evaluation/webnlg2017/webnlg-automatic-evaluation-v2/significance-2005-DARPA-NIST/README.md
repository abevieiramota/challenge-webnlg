author: Shashi Narayan

Significance test from the 2005 DARPA/NIST evaluation is used (Koehn and Monz's [paper](http://www.aclweb.org/anthology/W06-3114),
section 2.2, equation 3).

2005 DARPA/NIST evaluation

1) Randomly divide the test set in the blocks of 20 inputs, then
estimate document-level BLEU/TER/METEOR scores for each system for
each block.

2) Then for each pair of systems, we find k blocks on which one
performs better than the other.

3) Then we use the formula in the paper to estimate p-value.


The script prints out pairwise systems, difference (significant or not), k-value and p-value.

