#!/usr/bin/env python
#
# run as ./headergen.py infile.h outfile.h branchefs.py
# branchdefs.py must contain a list of branches named "process"
# or ./headergen.py this will set:
#  infile.h -> ../interface/ttbar_tree_template.h
#  outfile.h -> ../interface/ttbar_tree.h
#  branchdefs.py -> sample_branches.py
#
# author: Joosep Pata (ETHz) joosep.pata@cern.ch
# useful comments and ideas by Gregor Kasieczka (ETHz)
import sys, os, imp

#add type mappings from C++ -> ROOT 1-character here
typemap = {
    "float": "F",
    "int": "I",
}

#A branch representing a single number
#e.g. float met
class Scalar:
    #varname - name of variable in TTree and of the Branch
    def __init__(self, varname, type, needs_copy=False):
        self.varname = varname
        self.type = type
        self.needs_copy = needs_copy

    #returns variable definition
    def branchvar(self):
        return "%s %s" % (self.type, self.varname)

    #returns variable at loop initialization
    def initializer(self):
        return "%s = DEF_VAL_%s" % (self.varname, self.type.upper())

    #creates branch
    def creator(self):
        return "tree->Branch(\"%s\", &%s, \"%s/%s\")" % (
            self.varname,
            self.varname,
            self.varname,
            typemap[self.type]
        )

    #attaches existing branch
    def setaddress(self):
        return "tree->SetBranchAddress(\"%s\", &%s)" % (self.varname, self.varname)

    def copy_branch(self):
        return "{0} = itree->{0}".format(self.varname)

#A branch representing a fixed size 1D array
#e.g. float corrections[100]
class Static1DArray:
    #n - number or defined const static/define giving the size of the array
    def __init__(self, varname, type, n, needs_copy=False):
        self.varname = varname
        self.type = type
        self.n = n
        self.needs_copy = needs_copy

    def branchvar(self):
        return "%s %s[%s]" % (self.type, self.varname, self.n)

    def initializer(self):
        return "SET_ZERO(%s, %s, DEF_VAL_%s)" % (self.varname, self.n, self.type.upper())

    def creator(self):
        return "tree->Branch(\"%s\", %s, \"%s[%s]/%s\")" % (
            self.varname,
            self.varname,
            self.varname,
            self.n,
            typemap[self.type]
        )

    def setaddress(self):
        return "tree->SetBranchAddress(\"{0}\", {0})".format(self.varname)

    def copy_branch(self):
        return "std::copy(std::begin(itree->{0}), std::end(itree->{0}), std::begin({0}))".format(self.varname)


class Static2DArray:
    #n, m - compile-time constants giving the size of the array
    def __init__(self, varname, type, n, m, needs_copy=False):
        self.varname = varname
        self.type = type
        self.n = n
        self.m = m
        self.needs_copy = needs_copy

    def branchvar(self):
        return "%s %s[%s][%s]" % (self.type, self.varname, self.n, self.m)

    def initializer(self):
        return "SET_ZERO_2(%s, %s, %s, DEF_VAL_%s)" % (
            self.varname, self.n, self.m, self.type.upper()
        )

    def creator(self):
        return "tree->Branch(\"%s\", %s, \"%s[%s][%s]/%s\")" % (
            self.varname,
            self.varname,
            self.varname,
            self.n,
            self.m,
            typemap[self.type]
        )

    def setaddress(self):
        return "tree->SetBranchAddress(\"%s\", %s)" % (self.varname, self.varname)

    def copy_branch(self):
        return "std::copy(std::begin(itree->{0}), std::end(itree->{0}), std::begin({0}))".format(self.varname)


#dynamic-size 1D array, length varies across entries and is given by a branch.
class Dynamic1DArray:

    #n - branch name giving the length
    #maxlength - size of buffer
    def __init__(self, varname, type, n, maxlength, needs_copy=False):
        self.varname = varname
        self.type = type
        self.n = n
        self.maxlength = maxlength
        self.needs_copy = needs_copy

    def branchvar(self):
        return "%s %s[%s]" % (self.type, self.varname, self.maxlength)

    def initializer(self):
        return "SET_ZERO(%s, %s, DEF_VAL_%s)" % (self.varname, self.maxlength, self.type.upper())

    def creator(self):
        return "tree->Branch(\"%s\", %s, \"%s[%s]/%s\")" % (
            self.varname,
            self.varname,
            self.varname,
            self.n,
            typemap[self.type]
        )

    def setaddress(self):
        return "tree->SetBranchAddress(\"%s\", %s)" % (self.varname, self.varname)

    def copy_branch(self):
        return "std::copy(std::begin(itree->{0}), std::end(itree->{0}), std::begin({0}))".format(self.varname)


#list of all branches to add, modified by imports
process = []

#list of define statements to add
defines = []

if __name__ == "__main__":

    if len(sys.argv) == 4:
        filename_in = sys.argv[1]
        filename_out = sys.argv[2]
        filename_branches = sys.argv[3]
    else:
        print "Invalid number of arguments. Exiting..."
        print "Example: ./headergen.py template.h outfile.h branches.py" 
        print "try: ./headergen.py ../interface/tree_template.hh ../interface/tree.hh branches.py" 
        sys.exit()
    print "loading template", filename_in
    print "output file", filename_out
    print "branch file", filename_branches

    imp.load_source("branches", filename_branches)
    import branches
    branches_to_add = branches.process
    defines_to_add = branches.defines
    infile = open(filename_in)

    lines = infile.readlines()

    def insert_to(key_string, added_lines):
        i = 0
        for li in lines:
            if key_string in li:
                idx = i
                break
            i += 1
        lines.insert(idx, added_lines)

    for branch in branches_to_add:
        insert_to("//HEADERGEN_BRANCH_VARIABLES",
                  "\t%s;\n" % (branch.branchvar())
        )

        insert_to("//HEADERGEN_BRANCH_INITIALIZERS",
                  "\t\t%s;\n" % (branch.initializer())
        )

        insert_to("//HEADERGEN_BRANCH_CREATOR",
                  "\t\t%s;\n" % (branch.creator())
        )

        insert_to("//HEADERGEN_BRANCH_SETADDRESS",
              "\t\t%s;\n" % (branch.setaddress())
        )

        if branch.needs_copy and "//HEADERGEN_COPY_BRANCHES" in "".join(lines):
            insert_to("//HEADERGEN_COPY_BRANCHES",
                  "\t\t%s;\n" % (branch.copy_branch())
            )

    # Also allow inserting define statements
    for define in defines_to_add:
        print "Adding: ", define
        insert_to("//HEADERGEN_DEFINES", define + "\n"
        )


    outfile = open(filename_out, "w")
    for line in lines:
        outfile.write(line)
    outfile.close()
