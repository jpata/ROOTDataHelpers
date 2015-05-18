#include <iostream>
#include <TFile.h>
#include "interface/tree.hh"

int main(int argc, const char** argv) {
    std::cout << "testing tree.hh" << std::endl;
    
    //Create TTree if does not exist
    const char* fn = "";
    if (argc == 1) {
        TFile of("test.root", "RECREATE");
        of.cd();
        
        TTree _tree("tree", "tree");
        Tree tree(&_tree);
        tree.make_branches();
        for (int i=0; i<100; i++) {
            tree.loop_initialize();
            tree.n__jet = i;
            _tree.Fill();
        }
        of.Write();
        of.Close();
        fn = "test.root";
    } else {
        //Load from file
        fn = argv[1];
    }    
    TFile inf(fn);
    TTree* _tree = (TTree*)inf.Get("tree");
    
    Tree tree(_tree);
    tree.set_branch_addresses();
    for (int i=0; i<_tree->GetEntries(); i++) {
        tree.loop_initialize(); 
        _tree->GetEntry(i);
        //std::cout << tree.n__jet << std::endl;
    }
    inf.Close();

    return 0;
}
