#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
#include <TFile.h>
#include <TTree.h>
#include <TMVA/Factory.h>
#include <TMVA/Reader.h>
#include <interface/AutoTree.hh>

#include <string>
#include <sstream>
#include <vector>

using namespace std;

int exit_with_message(const char* message, int code) {
    cerr << message << endl;
    return code;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        return exit_with_message("./mva config.ini", 0);
    }
    
    boost::property_tree::ptree pt;
    boost::property_tree::ini_parser::read_ini(argv[1], pt);

    const string tree_fn = pt.get<string>("Input.data_filename");
    const string tree_name = pt.get<string>("Input.tree_name");

    const string mvas = pt.get<string>("Input.mvas");
    
    TFile infile(tree_fn.c_str());
    if (infile.IsZombie()) {
        return exit_with_message("Could not open file", 1);
    }
    TTree* tree = (TTree*)infile.Get(tree_name.c_str());
    if (tree == 0) {
        return exit_with_message("Could not open tree", 1);
    }
    AutoTree atree(tree);
    cout << atree.getTreeStructure().toString();
    atree.getEntry(0);
    
    vector<string> mva_vec = split(mvas, ',');
    map<string, TMVA::Reader*> readers;
    
    TreeStructure outStructure;
    
    for (auto& mva_name : mva_vec) {
        auto& mva_sec = pt.get_child(mva_name);
        const string weight_fn = mva_sec.get<string>("weight_filename");
        
        const string vars_tree = mva_sec.get<string>("tree_variables");
        const string vars_mva = mva_sec.get<string>("mva_variables");
        const vector<string> vars_tree_vec = split(vars_tree, ',');
        const vector<string> vars_mva_vec = split(vars_mva, ',');
        
        const string specs_tree = mva_sec.get<string>("tree_spectators");
        const string specs_mva = mva_sec.get<string>("mva_spectators");
        const vector<string> specs_tree_vec = split(specs_tree, ',');
        const vector<string> specs_mva_vec = split(specs_mva, ',');
        if (specs_tree_vec.size() != specs_mva_vec.size()) {
            return exit_with_message("mismatch in tree-mva spectators", 1);
        }
        
        readers[mva_name] = new TMVA::Reader("!V:Silent");
        for (unsigned int i=0; i<vars_tree_vec.size(); i++) {
            float* p = atree.getAddress<float>(vars_tree_vec[i]);
            if (p == 0) {
                return exit_with_message((string("could not find branch ")+vars_tree_vec[i]).c_str(), 1);
            }
            readers[mva_name]->AddVariable(
                vars_mva_vec[i].c_str(),
                p
            );
            outStructure.branches[mva_name] = BranchType(BranchType::Type::FLOAT);
        }
        for (unsigned int i=0; i<specs_tree_vec.size(); i++) {
            float* p = atree.getAddress<float>(specs_tree_vec[i]);
            if (p == 0) {
                return exit_with_message((string("could not find branch ")+vars_tree_vec[i]).c_str(), 1);
            }
            readers[mva_name]->AddSpectator(
                specs_mva_vec[i].c_str(),
                p
            );
        }

        readers[mva_name]->BookMVA(mva_name.c_str(), weight_fn.c_str());
    }
    
    TFile outfile(pt.get<string>("Output.filename").c_str(), "RECREATE");
    AutoTree outtree(outStructure, pt.get<string>("Output.tree_name"));
    
    for(unsigned int iev=0; iev < atree.tree->GetEntries(); iev++) {
        atree.getEntry(iev);
        for (auto& mva_name : mva_vec) {
            float mva = readers[mva_name]->EvaluateMVA(mva_name.c_str());
            outtree.floats_map[mva_name]->val = mva;
        }
        outtree.tree->Fill();
    }
    
    infile.Close();
    outfile.Write();
    outfile.Close();
    return 0;
}
