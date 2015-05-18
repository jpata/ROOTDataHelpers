ROOTDataHelpers
================

A collection of scripts to simplify data management in ROOT (http://root.cern.ch)

* headergen: based on a python list, generates header files for ROOT TTrees. 

headergen
----------

Very often, you want many similar branches for event variables: "jet_pt", "jet_eta" etc. To create the TTree by hand can be error-prone, therefore, it is useful to create the ttree header once automatically so that it's easy to update and use it in all the codes (ntuplizer, histogrammer).

Using headergen, you will get a header file which creates the branches and branch value holders, initializes the branches at each loop iteration and attaches the branches to an existing TTree.

You will be able to define branches in a python file:
~~~
#add vector branches
for x in ["lep", "jet"]:
    for t in ["pt", "eta", "phi", "pass"]:
        full_branch_name = "{0}__{1}".format(x, t)
        process += [
            Dynamic1DArray(full_branch_name, "float", "n__{0}".format(x), "N_MAX")
        ]
~~~

Later you can always create the tree with a few lines
~~~
#include "tree.hh"
...
TTree root_tree("tree", "tree");
Tree tree(&root_tree);
tree.make_branches();
for (int i=0;i<10;i++) {
  tree.loop_initialize();
  tree.event_index = 3;
  root_tree.Fill();
};
~~~

and also load it with a few lines
~~~
#include "tree.hh"
...
TTree root_tree("tree", "tree");
Tree tree(&root_tree);
tree.set_branch_addresses();
for (int i=0;i<10;i++) {
  tree.loop_initialize();
  root_tree.GetEntry(i);
  std::cout << "event " << tree.event_index << std::endl;
};
~~~

In short:

1. Define the TTree structure in `python/branches.py`
2. Create the header with`./python/headergen.py interface/tree_template.hh interface/tree.hh python/branches.py`
3. compile with `make testHeaderGen`
4. run `./testTreeHeader`
