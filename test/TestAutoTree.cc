#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "interface/AutoTree.hh"

int main(int argc, const char** argv) {
    std::cout << "testing AutoTree" << std::endl;
    
    //Create TTree if does not exist
    const char* fn = "";
    if (argc == 1) {
        TFile of("tf.root", "RECREATE");
        of.cd();
        
        int x_i = 0;
        TTree tree("tree", "tree");
        tree.Branch("x_i", &x_i, "x_i/I");
        
        for (int i=0; i<100; i++) {
            x_i = i;
            tree.Fill();
        }
        tree.Write();
        of.Close();
        fn = "tf.root";
    } else {
        //Load from file
        fn = argv[1];
    }    
    TFile inf(fn);
    TTree* ptree = (TTree*)inf.Get("tree");
    
    AutoTree atree(ptree);
    
    std::cout << atree.getTreeStructure().toString();
    return 0;
}
