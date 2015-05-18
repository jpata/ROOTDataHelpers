#ifndef ANALYSIS_TREE
#define ANALYSIS_TREE

#include <TTree.h>
#include <string>
#include <map>
#include <cmath>
#include <iostream>

#define N_MAX 500
#define M_MAX 100
#define T_MAX 100
#define MET_S_MAX 20

//these are simple 'sentinel values' for uninitialized variables
//for clarity, it would be best to use these instead of manually writing -99 etc.
//this way, undefined variables are always unique and one can write functions to recognize them
#define DEF_VAL_FLOAT -9999.0
#define DEF_VAL_DOUBLE -9999.0
#define DEF_VAL_INT -9999
#define FLOAT_EPS 0.0000001
#define DOUBLE_EPS 0.0000001

//HEADERGEN_DEFINES

//checks if a branch variable is undefined
inline bool is_undef(int x) { return x==DEF_VAL_INT; };
inline bool is_undef(float x) { return fabs(x-DEF_VAL_FLOAT) < FLOAT_EPS; };
inline bool is_undef(double x) { return fabs(x-DEF_VAL_DOUBLE) < DOUBLE_EPS; };

//macros to initialize 1D and 2D (square) arrays
//x is the array, n is the size, y is the initialized value
#define SET_ZERO(x,n,y) for(int i=0;i<n;i++) {x[i]=y;}
#define SET_ZERO_2(x,n,m,y) for(int i=0;i<n;i++) { for(int j=0;j<m;j++) { x[i][j]=y; } }

/*
This is a simple wrapper class for the a flat data format.
To use it, one should load the input file in the standard way using
TFile* f = new TFile("ntuple.root");
TTree* _ttree = (TTree*)f->Get("tree");
and then initialize the class using
Tree tree(_ttree);

Tree contains the C++ variables for all the branches and functions to conveniently set them.
To attach the branches in the read mode (call SetBranchAddress), call
tree.set_branch_addresses();
outside the event loop.
 You can loop over the events in the standard way

 for (unsigned int i=0; i < _ttree->GetEntries(); i++) {
     tree.loop_initialize(); // <-- this makes sure all the branch variables are cleared from the previous entry
     _ttree->GetEntry(i); // <--- loads the branch contents into the branch variables

     for (int njet=0; njet < tree.n__jet; njet++) {
         float x = tree.jet__pt[njet];
         //do something with the jet pt 
     }
*/
class Tree {
public:
    Tree(TTree* _tree) { tree = _tree; };
	TTree* tree;
   
        // Helper functions for accessing branches
	template <typename T> 
	T get_address(const std::string name) {
		auto* br = tree->GetBranch(name.c_str());
		if (br==0) {
			std::cerr << "ERROR: Tree::get_address " << "branch " << name << " does not exist" << std::endl;
			throw std::exception();
		}
		auto* p = br->GetAddress();
		return reinterpret_cast<T>(p);
	}
    
	float weight__genmc;
	int n__jet;
	int n__lep;
	float lep__pt[N_MAX];
	float lep__eta[N_MAX];
	float lep__phi[N_MAX];
	float lep__pass[N_MAX];
	float jet__pt[N_MAX];
	float jet__eta[N_MAX];
	float jet__phi[N_MAX];
	float jet__pass[N_MAX];
    //HEADERGEN_BRANCH_VARIABLES
    //This comment is for automatic header generation, do not remove

    //initializes all branch variables
	void loop_initialize(void) {
		weight__genmc = DEF_VAL_FLOAT;
		n__jet = DEF_VAL_INT;
		n__lep = DEF_VAL_INT;
		SET_ZERO(lep__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__pass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__pass, N_MAX, DEF_VAL_FLOAT);
        //HEADERGEN_BRANCH_INITIALIZERS
        //This comment is for automatic header generation, do not remove
	}

    //makes branches on a new TTree
	void make_branches(void) {
		tree->Branch("weight__genmc", &weight__genmc, "weight__genmc/F");
		tree->Branch("n__jet", &n__jet, "n__jet/I");
		tree->Branch("n__lep", &n__lep, "n__lep/I");
		tree->Branch("lep__pt", lep__pt, "lep__pt[n__lep]/F");
		tree->Branch("lep__eta", lep__eta, "lep__eta[n__lep]/F");
		tree->Branch("lep__phi", lep__phi, "lep__phi[n__lep]/F");
		tree->Branch("lep__pass", lep__pass, "lep__pass[n__lep]/F");
		tree->Branch("jet__pt", jet__pt, "jet__pt[n__jet]/F");
		tree->Branch("jet__eta", jet__eta, "jet__eta[n__jet]/F");
		tree->Branch("jet__phi", jet__phi, "jet__phi[n__jet]/F");
		tree->Branch("jet__pass", jet__pass, "jet__pass[n__jet]/F");
        //HEADERGEN_BRANCH_CREATOR
        //This comment is for automatic header generation, do not remove
	}

    //connects the branches of an existing TTree to variables
    //used when loading the file
	void set_branch_addresses(void) {
		tree->SetBranchAddress("weight__genmc", &weight__genmc);
		tree->SetBranchAddress("n__jet", &n__jet);
		tree->SetBranchAddress("n__lep", &n__lep);
		tree->SetBranchAddress("lep__pt", lep__pt);
		tree->SetBranchAddress("lep__eta", lep__eta);
		tree->SetBranchAddress("lep__phi", lep__phi);
		tree->SetBranchAddress("lep__pass", lep__pass);
		tree->SetBranchAddress("jet__pt", jet__pt);
		tree->SetBranchAddress("jet__eta", jet__eta);
		tree->SetBranchAddress("jet__phi", jet__phi);
		tree->SetBranchAddress("jet__pass", jet__pass);
        //HEADERGEN_BRANCH_SETADDRESS
        //This comment is for automatic header generation, do not remove
	}
};

#endif
