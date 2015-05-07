import ROOT, sys
from treeWrapperGen import get_tree_structure


def makearraytype(arrayname, arraytype, arraysize):
    s = "hsize_t ${arrayname}_dim[] = {${arraysize}};" + nl
    s += "hid_t ${arrayname}_type = H5Tarray_create(${typemap[$arraytype]}, 1, ${arrayname}_dim);" + nl

# function arraytypename
# {
#     arrayname=$1
#     echo "${arrayname}_type"
# }

typemap = {}
typemap["Char_t"] = "H5T_NATIVE_CHAR"
typemap["UChar_t"] = "H5T_NATIVE_UCHAR"
typemap["Short_t"] = "H5T_NATIVE_SHORT"
typemap["UShort_t"] = "H5T_NATIVE_USHORT"
typemap["Int_t"] = "H5T_NATIVE_INT"
typemap["UInt_t"] = "H5T_NATIVE_UINT"
typemap["Long_t"] = "H5T_NATIVE_LONG"
typemap["ULong_t"] = "H5T_NATIVE_ULONG"
typemap["Float_t"] = "H5T_NATIVE_FLOAT"
typemap["Double_t"] = "H5T_NATIVE_DOUBLE"
    
filename = sys.argv[1]
treename = sys.argv[2]

tf = ROOT.TFile(filename)
tt = tf.Get(treename)

tt.MakeClass("TreeClass")

tree_structure, tree_structure_by_count = get_tree_structure(tt)
branchnames = sorted(tree_structure.keys())

s = ""
nl = "\n"

s += "#include <TFile.h>" + nl
s += "#include <TTree.h>" + nl
s += "#include <iostream>" + nl
s += "#include \"treeclass.h\"" + nl
s += "extern \"C\" {" + nl
s += "#include <hdf5.h>" + nl
s += "}" + nl

# event struct:
s += "struct event {" + nl
for br in branchnames:
    s += "  {0} {1};".format(typemap[tree_structure[br][0][1]], br) + nl
s +=  "};" + nl

# event copy function:
s +=  "void copy_event(TreeClass& treeclass, event& e)" + nl
s +=  "{ //scalars:" + nl
for br, btype, count in tree_structure_by_count["scalar"]:
    s +=  "  e.{0} = treeclass.{0};".format(br) + nl
s += "}" + nl
s +=  "//arrays:" + nl
#for((i=0;i<${#arrays[@]};i=(i+1))); do
#    s +=  "for(int i = 0; i < ${arraysizes[i]}; ++i) e.${arrays[i]}[i] = treeclass_event.${arrays[i]}[i];" + nl
# done;
# s +=  "}" + nl
# 
# Start of main:
s +=  "int main(int argc, char** argv)" + nl
s +=  "{" + nl
s +=  "  if(argc != 3) {" + nl
s +=  "    std::cerr << \"Usage: $(basename $converter_prog) <input_file.root> <output_file.h5>\"" + nl
s +=  "    << std::endl;" + nl
s +=  "    return 1;" + nl
s +=  "  }" + nl

# Open input file:
s +=  "  TFile infile(argv[1],\"read\");" + nl
s +=  "  TTree* tree;" + nl
s +=  "  infile.GetObject(\"$treename\",tree);" + nl

# Setup Branches:
s +=  "  TreeClass treeclass(tree);" + nl

s +=  "  hsize_t numevents = tree->GetEntries();" + nl
s +=  "  if (numevents <= 0)" + nl
s +=  "    return 1;" + nl

s +=  "  event* buffer = new event[numevents];" + nl
s +=  "  hid_t file, dataset, space, memspace, cparms;" + nl
s +=  "  herr_t status;" + nl
s +=  "  hsize_t dataspace_dim[] = {numevents};" + nl
s +=  "  hsize_t dataspace_maxdim[] = {numevents};" + nl
# this doesn't seem consistent with writing all events at once
s +=  "  hsize_t slabsize[] = {1};" + nl
s +=  "  hsize_t chunkdim[] = {numevents};" + nl
s +=  "  space = H5Screate_simple(1,dataspace_dim,dataspace_maxdim);" + nl
s +=  "  file = H5Fcreate(argv[2],H5F_ACC_TRUNC,H5P_DEFAULT,H5P_DEFAULT);" + nl
s +=  "  cparms = H5Pcreate(H5P_DATASET_CREATE);" + nl
s +=  "  status = H5Pset_chunk(cparms,1,chunkdim);" + nl
s +=  "  status = H5Pset_deflate(cparms,1);" + nl

# # Create array datatypes:
# for((i=0; i<${#arrays[@]}; i=(i+1))); do
#     makearraytype ${arrays[i]} ${arraytypes[i]} ${arraysizes[i]}
# done
# 
# # Create compound type:
s +=  "  hid_t event_tid;" + nl
s +=  "  event_tid = H5Tcreate(H5T_COMPOUND, sizeof(event));" + nl
# # Insert members:
# for((i=0; i<${#rawvars[@]}; i=(i+1))); do
#     if [[ $(s +=  ${rawvars[i]} | grep '\[') == "" ]] ; then
#         # scalar
#         s +=  "H5Tinsert(event_tid,\"${rawvars[i]}\", HOFFSET(event, ${rawvars[i]}), ${typemap[${types[i]}]});"
#     else
#         # array
#         arrayname=$(s +=  ${rawvars[i]} | sed -e 's/\[.*\]//')
#         s +=  "H5Tinsert(event_tid,\"$arrayname\", HOFFSET(event, $arrayname), $(arraytypename $arrayname));"
#     fi
# done
# 
# # Create dataset
s +=  "  dataset = H5Dcreate1(file,\"{0}\",event_tid,space,cparms);".format(treename) + nl
# # Create memspace
s +=  "  memspace = H5Screate_simple(1,slabsize,0);" + nl
s +=  "  hsize_t slab_block_count[] = {1};" + nl

# # Conversion loop:
s +=  "  for(int row=0; row<numevents; ++row) {" + nl
s +=  "    tree->GetEvent(row);" + nl
s +=  "    copy_event(treeclass_event,buffer[row]);" + nl
s +=  "  }" + nl
# 
# Write to dataset
s +=  "  space = H5Dget_space(dataset);" + nl
s +=  "  status = H5Dwrite(dataset,event_tid,H5S_ALL,H5S_ALL,H5P_DEFAULT,buffer);" + nl
s +=  "  status = H5Sclose(space);" + nl

# Cleanup
s +=  "  status = H5Pclose(cparms);" + nl
s +=  "  status = H5Tclose(event_tid);" + nl
s +=  "  status = H5Sclose(memspace);" + nl
s +=  "  status = H5Dclose(dataset);" + nl
s +=  "  status = H5Fclose(file);" + nl
s +=  "  infile.Close();" + nl
s +=  "  return 0;" + nl
s +=  "}" + nl
print s
