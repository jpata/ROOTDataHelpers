import ROOT, sys
ROOT.gROOT.SetBatch(True)

tf = ROOT.TFile(sys.argv[1])
tt = tf.Get(sys.argv[2])

for br in tt.GetListOfBranches():
    bn = br.GetName()
    bleaves = [(l.GetName(), l.GetTypeName()) for l in br.GetListOfLeaves()]
    
    print bn, bleaves
