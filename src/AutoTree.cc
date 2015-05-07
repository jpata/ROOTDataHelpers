#include "interface/AutoTree.hh"

AutoTree::AutoTree(TTree* tree) {
    this->tree = tree;
    TObjArray* brlist = tree->GetListOfBranches();
    for (int i=0; i<brlist->GetEntries(); i++) {
        TBranch* br = (TBranch*)brlist->At(i);
        TObjArray* leaves = br->GetListOfLeaves();
        for (int j=0; j<leaves->GetEntries(); j++) {
            TLeaf* leaf = (TLeaf*)leaves->At(j);
            const std::string leaf_name(leaf->GetName());
            const std::string cn(leaf->GetTypeName());
            //const int len_type = leaf->GetLenType();
            //const int len_static = leaf->GetLenStatic();
            int countval = 0;
            const TLeaf* leaf_counter =  leaf->GetLeafCounter(countval);
            if (leaf_counter != 0) {
                const std::string length_name(leaf_counter->GetName());
                if (cn == "Double_t") {
                    vdoubles_map[leaf_name] = new VariableArrayBranch<double>(length_name);
                    //tree->SetBranchAddress(leaf_counter->GetName(), &vdoubles_map[leaf_name].n);
                    tree->SetBranchAddress(leaf_name.c_str(), vdoubles_map[leaf_name]->val);
                    
                    tree_structure.insert(leaf_name, BranchType(BranchType::Type::VDOUBLE));
                }
                else if (cn == "Float_t") {
                    vfloats_map[leaf_name] = new VariableArrayBranch<float>(length_name);
                    //tree->SetBranchAddress(leaf_counter->GetName(), &vfloats_map[leaf_name].n);
                    tree->SetBranchAddress(leaf_name.c_str(), vfloats_map[leaf_name]->val);
                    
                    tree_structure.insert(leaf_name, BranchType(BranchType::Type::VFLOAT));
                }
                else if (cn == "Int_t") {
                    vints_map[leaf_name] = new VariableArrayBranch<int>(length_name);
                    //tree->SetBranchAddress(leaf_counter->GetName(), &vints_map[leaf_name].n);
                    tree->SetBranchAddress(leaf_name.c_str(), vints_map[leaf_name]->val);
                    
                    tree_structure.insert(leaf_name, BranchType(BranchType::Type::VINT));
                }
                //std::cout << leaf_name << "/" << cn << "[" << length_name << "]" << std::endl;
            } else {
                if (cn == "Double_t") {
                    doubles_map[leaf_name] = new ScalarBranch<double>();
                    tree->SetBranchAddress(leaf_name.c_str(), &doubles_map[leaf_name]->val);
                    tree_structure.insert(leaf_name, BranchType(BranchType::Type::DOUBLE));
                }
                else if (cn == "Float_t") {
                    floats_map[leaf_name] = new ScalarBranch<float>();
                    tree->SetBranchAddress(leaf_name.c_str(), &floats_map[leaf_name]->val);
                    tree_structure.insert(leaf_name, BranchType(BranchType::Type::FLOAT));
                }
                else if (cn == "Int_t") {
                    ints_map[leaf_name] = new ScalarBranch<int>();
                    tree->SetBranchAddress(leaf_name.c_str(), &ints_map[leaf_name]->val);
                    tree_structure.insert(leaf_name, BranchType(BranchType::Type::INT));
                }
                //std::cout << leaf_name << "/" << cn << std::endl;
            }
        }
    }
}
    
unsigned long AutoTree::getEntry(unsigned long i) {
    for (auto kv : doubles_map) {
        kv.second->zero();
    }
    for (auto kv : vdoubles_map) {
        kv.second->zero();
    }
    for (auto kv : floats_map) {
        kv.second->zero();
    }
    for (auto kv : vfloats_map) {
        kv.second->zero();
    }
    for (auto kv : ints_map) {
        kv.second->zero();
    }
    for (auto kv : vints_map) {
        kv.second->zero();
    }
    
    return tree->GetEntry(i);
}

template <>
double AutoTree::getValue<double>(const std::string name) {
    assert(doubles_map.find(name) != doubles_map.end());
    return doubles_map[name]->val;
}

template <>
float AutoTree::getValue<float>(const std::string name) {
    assert(floats_map.find(name) != floats_map.end());
    return floats_map[name]->val;
}

template <>
int AutoTree::getValue<int>(const std::string name) {
    assert(ints_map.find(name) != ints_map.end());
    return ints_map[name]->val;
}

template <>
vector<double> AutoTree::getValue<vector<double>>(const std::string name) {
    assert(vdoubles_map.find(name) != vdoubles_map.end());
    assert(ints_map.find(vdoubles_map[name]->length_name) != ints_map.end());
    vector<double> ret;
    for (int i=0; i<ints_map[vdoubles_map[name]->length_name]->val; i++) {
        ret.push_back(vdoubles_map[name]->val[i]);
    }
    return ret;
}

template <>
vector<float> AutoTree::getValue<vector<float>>(const std::string name) {
    assert(vfloats_map.find(name) != vfloats_map.end());
    assert(ints_map.find(vfloats_map[name]->length_name) != ints_map.end());
    vector<float> ret;
    for (int i=0; i<ints_map[vfloats_map[name]->length_name]->val; i++) {
        ret.push_back(vfloats_map[name]->val[i]);
    }
    return ret;
}

template <>
vector<int> AutoTree::getValue<vector<int>>(const std::string name) {
    assert(vints_map.find(name) != vints_map.end());
    assert(ints_map.find(vints_map[name]->length_name) != ints_map.end());
    vector<int> ret;
    for (int i=0; i<ints_map[vints_map[name]->length_name]->val; i++) {
        ret.push_back(vints_map[name]->val[i]);
    }
    return ret;
}
