import ROOT, sys

def get_tree_structure(tt):
    brlist = tt.GetListOfBranches()
    brnames = sorted([b.GetName() for b in brlist])
    tree_structure = {}

    for bn in brnames:
        br = tt.GetBranch(bn)
        leaves = list(br.GetListOfLeaves())
        nleaves = len(leaves)
        if nleaves != 1:
            print "ERROR: ", bn, nleaves
            continue
        leaf = leaves[0]
        count = leaf.GetLeafCount()
        count_static = leaf.GetLenStatic()
        if count != None:
            count_name = count.GetName()
            count_type = count.GetTypeName()
        elif count_static != 1:
            count_name = "staticarray"
            count_type = count_static
        else:
            count_name = "scalar"
            count_type = None
        tree_structure[bn] = ((bn, leaf.GetTypeName()), (count_name, count_type))
        #print bn, leaf, count, leaf.GetTypeName()

    tree_structure_by_count = {}
    for (k, v) in tree_structure.items():
        ((bn, btype), (cn, ctype)) = v
        if not tree_structure_by_count.has_key(cn):
            tree_structure_by_count[cn] = []
        tree_structure_by_count[cn].append(
            (bn, btype, ctype)
        )
    return tree_structure, tree_structure_by_count

if __name__ == "__main__":
    
    tf = ROOT.TFile(sys.argv[1])
    tt = tf.Get(sys.argv[2])

    tree_structure, tree_structure_by_count = get_tree_structure(tt)
    ev = "class Event:\n"
    ev += "  def __init__(self, tree):\n"

    for k in sorted(tree_structure_by_count.keys()):
        #print k, tree_structure_by_count[k]
        
        s = ""
        if k not in ["scalar"]:
            class_name = k[1:]
            s += "class " + class_name + ":\n"
            
            typemap = "  types = {\n"
            
            s += "  def __init__(self, tree, i):\n"
            for (br, btype, ctype) in tree_structure_by_count[k]:
                brname = br[br.find("_")+1:]
                s += "    self.{0} = tree.{1}[i]\n".format(brname, br)
                typemap += "    '{0}': '{1}',\n".format(brname, btype)
            typemap += "  }\n"
            
            if k == "staticarray":
                count = ctype
            else:
                count = "tree."+k
            
            s += typemap
            
            s += "\n"
            s += "  @staticmethod\n"
            s += "  def make_array(tree):\n"
            s += "    return [{0}(tree, i) for i in range({1})]\n".format(
                class_name, count
            )
            
            ev += "    self.{0} = {0}.make_array(tree)\n".format(class_name)
        else:
            for (br, brtype, ctype) in tree_structure_by_count[k]:
                ev += "    self.{0} = tree.{0}\n".format(br)
        
        print s

    print ev
