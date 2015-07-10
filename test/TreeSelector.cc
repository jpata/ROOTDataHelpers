#include <TFile.h>
#include <TTree.h>
#include <interface/AutoTree.hh>

#include <string>
#include <sstream>
#include <vector>
#include <algorithm>    // std::random_shuffle
#include <ctime>        // std::time
#include <cstdlib>      // std::rand, std::srand

using namespace std;

int exit_with_message(const char* message, int code) {
    cerr << message << endl;
    return code;
}

int main(int argc, char** argv) {
    std::srand ( unsigned ( std::time(0) ) );

    if (argc != 5) {
        return 1;
    }
    
    const string tree_fn = argv[1];
    const string tree_name = argv[2];
    const string out_fn = argv[3];
    const long nmax = std::stol(argv[4]);

    TFile infile(tree_fn.c_str());
    if (infile.IsZombie()) {
        return exit_with_message("Could not open file", 1);
    }
    TTree* tree = (TTree*)infile.Get(tree_name.c_str());
    if (tree == 0) {
        return exit_with_message("Could not open tree", 1);;
    }
    AutoTree atree(tree);
    
    TFile outfile(out_fn.c_str(), "RECREATE");
    TTree* outtree = new TTree(tree_name.c_str(), tree_name.c_str());
    atree.createBranches(outtree);
    atree.connectBranches(outtree);
    
    std::vector<unsigned long> entrylist;
    for(unsigned long iev=0; iev < atree.tree->GetEntries(); iev++) {
        entrylist.push_back(iev);
    }
    std::cout << "Shuffling " << atree.tree->GetEntries() << " events..." << std::endl;
    std::random_shuffle ( entrylist.begin(), entrylist.end() );
    std::sort(entrylist.begin(), entrylist.end());
    std::cout << "Looping over " << nmax << " events..." << std::endl;
    
    for(unsigned long i=0; i < nmax; i++) {
        unsigned long iev = entrylist[i];
        atree.getEntry(iev);
        outtree->Fill();
    }
    
    infile.Close();
    outfile.Write();
    outfile.Close();
    return 0;
}
