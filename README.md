ROOTDataHelpers
================

A collection of scripts to simplify data management in ROOT (http://root.cern.ch)

* headergen: based on a python list, generates header files for ROOT TTrees.



headergen
----------
1. Define the TTree structure in `python/branches.py`
2. Create the header with`./python/headergen.py interface/tree_template.hh interface/tree.hh python/branches.py`
3. compile with `make testHeaderGen`
4. run `./testTreeHeader`
