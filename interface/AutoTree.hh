#pragma once
#include <map>
#include "TTree.h"
#include "TLeaf.h"
#include "TFile.h"

#include <iostream>
#include <sstream>
#include <assert.h>
#include <stdexcept>

using namespace std;

#define MAX_ARRAY_SIZE 500
#define DEF_VAL 0

template <class T>
class ScalarBranch {
public:
    
    //buffer for SetBranchAddress
    T val = 0;
    
    ScalarBranch() {
        zero();
    }
    void zero() {
        val = (T)0;
    }
};

template <class T>
class VariableArrayBranch {
public:
    
    //buffer for SetBranchAddress
    T val[MAX_ARRAY_SIZE];
    
    //Name of the branch that contains the length.
    const std::string length_name;
    
    //Clear buffers
    void zero() {
        for (int i=0; i<MAX_ARRAY_SIZE; i++) {
            val[i] = (T)DEF_VAL;
        }
    }    
    
    VariableArrayBranch(const std::string _length_name) :
    length_name(_length_name) {
    }
};


class BranchType {
    
public:
    
    enum Type {
        UNKNOWN,
        DOUBLE,
        FLOAT,
        INT,
        VDOUBLE,
        VFLOAT,
        VINT,
    };
    
    Type type;
    
    BranchType(Type _type) : type(_type) {};
    BranchType() : type(UNKNOWN) {};
    
    const std::string toString() const {
        std::stringstream ss;
        ss << "type " << type;
        return ss.str();
    }
};


vector<string> &split(const string &s, char delim, vector<string> &elems);
vector<string> split(const std::string &s, char delim);

class TreeStructure {
public:
    
    std::map<const std::string, BranchType> branches;    

    TreeStructure() {
        
    }
    
    TreeStructure(const std::string& description) {
        std::vector<std::string> tokens = split(description, ':');
        for (auto& tok : tokens) {
            std::vector<std::string> tok_vec = split(tok, '/');
            if (tok_vec.size()!=2) {
                throw std::runtime_error("could not understand token");
            }
            const std::string name = tok_vec[0];
            const std::string type = tok_vec[1];
            
            if (type == "F") {
                branches[name] = BranchType(BranchType::Type::FLOAT);
            } else {
                throw std::runtime_error("could not understand token type");
            }
        }
    }
    const std::string toString() const {
        std::stringstream ss;
        for (auto& kv : branches) {
            ss << kv.first << ": " << kv.second.toString() << std::endl;
        }
        return ss.str();
    }
    
    void insert(const std::string branch_name, BranchType type) {
        branches.insert(std::pair<std::string, BranchType>(branch_name, type));
    }
};

class AutoTree {
private:
    TreeStructure tree_structure;
public:
    
    //Double and double array buffers
    std::map<const std::string, ScalarBranch<double>*>          doubles_map;
    std::map<const std::string, VariableArrayBranch<double>*>   vdoubles_map;
    
    //Float and float array buffers
    std::map<const std::string, ScalarBranch<float>*>           floats_map;
    std::map<const std::string, VariableArrayBranch<float>*>    vfloats_map;
    
    //Int and int array buffers
    std::map<const std::string, ScalarBranch<int>*>             ints_map;
    std::map<const std::string, VariableArrayBranch<int>*>      vints_map;
    TTree* tree;
    
    AutoTree(TreeStructure&&, const std::string& );
    AutoTree(TTree*);

    unsigned long getEntry(unsigned long i);
    void createBranches(TTree* tree);
    void connectBranches(TTree* tree);
    
    template <class T>
    T getValue(const std::string name);

    template <class T>
    T* getAddress(const std::string name);
    
    const TreeStructure getTreeStructure() {
        return tree_structure;
    }
    
    
};
