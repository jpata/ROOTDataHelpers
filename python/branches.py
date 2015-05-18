#sample branches file for headergen.py
#uses branch classes from headergen
from headergen import *

#add additional defines
defines.extend([])

#add a scalar branch
process += Scalar("weight__genmc", "float"),

process += Scalar("n__jet", "int"),
process += Scalar("n__lep", "int"),

#add vector branches
for x in ["lep", "jet"]:
    for t in ["pt", "eta", "phi", "pass"]:
        full_branch_name = "{0}__{1}".format(x, t)
        process += [
            Dynamic1DArray(full_branch_name, "float", "n__{0}".format(x), "N_MAX")
        ]

