from sklearn.externals import six
from sklearn.tree import _tree

def node_to_str(cls, tree, node_id, criterion, depth, kind):
    if not isinstance(criterion, six.string_types):
        criterion = "impurity"

    value = tree.value[node_id]
    if tree.n_outputs == 1:
        value = value[0, :]
    
    cType = 1
    IVar = 0
    cut = 0.0
    
    if tree.children_left[node_id] == _tree.TREE_LEAF:
        IVar = -1
        return '<Node pos="{0}" depth="{1}" NCoef="0" \
IVar="{2}" Cut="{3:.16E}" cType="1" \
res="{4:.16E}" rms="0.0e-00" \
purity="{5}" nType="-99"/>'.format(
            kind, depth, IVar, 0.0, value[0]*cls.learning_rate,
            1.0 - tree.impurity[node_id]
        )
    else:
        IVar = tree.feature[node_id]
        return '<Node pos="{0}" depth="{1}" NCoef="0" \
IVar="{2}" Cut="{3:.16E}" cType="1" \
res="{4:.16E}" rms="0.0" \
purity="{5}" nType="0">'.format(
        kind, depth, IVar, tree.threshold[node_id], value[0]*cls.learning_rate,
        1.0 - tree.impurity[node_id]
    )

def recurse(cls, outfile, t, node_id=0, criterion="impurity", depth=0, kind=""):   
    outfile.write(depth*"  "+node_to_str(cls, t, node_id, criterion, depth, kind) + '\n')
    left_child = t.children_left[node_id]
    right_child = t.children_right[node_id]
    if depth == 10:
        return
    if left_child != _tree.TREE_LEAF:
        recurse(cls, outfile, t, left_child, criterion, depth+1, kind="l")
        recurse(cls, outfile, t, right_child, criterion, depth+1, kind="r")
    if left_child != _tree.TREE_LEAF:
        outfile.write(depth*"  "+"</Node>\n")
    
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
def gbr_to_tmva(cls, data, outfile_name, **kwargs):
    if not isinstance(cls, GradientBoostingRegressor):
        raise ValueError("Can only export GradientBoostingRegressor")
    if cls.loss != "huber":
        raise ValueError("TMVA assumes loss=huber")
    if cls.n_classes_ != 1:
        raise ValueError("Currently only two-class classification supported. (regression between 0 and 1).")    
    mva_name = kwargs.get("mva_name", "testmva")
    feature_names = data.columns.values
    features_min  = [data[fn].min() for fn in feature_names]
    features_max  = [data[fn].max() for fn in feature_names]
    
    #Create list of variables
    varstring = ""
    for i in range(cls.n_features):
        varstring += '<Variable VarIndex="{0}" Expression="{1}" Label="{1}" Title="{1}" Unit="" Internal="{1}" Type="F" Min="{2:.16E}" Max="{3:.16E}"/>\n'.format(
            i, feature_names[i], features_min[i], features_max[i]
        )


    outfile = open(outfile_name, "w")
    outfile.write(
    """
    <?xml version="1.0"?>
    <MethodSetup Method="BDT::{mva_name}">
    <GeneralInfo>
    <Info name="TMVA Release" value="4.2.0 [262656]"/>
    <Info name="ROOT Release" value="6.02/05 [393733]"/>
    <Info name="Creator" value="joosep"/>
    <Info name="Date" value="Sun May 31 01:31:49 2015"/>
    <Info name="Host" value="Linux cmsbuild13.cern.ch 2.6.32-504.8.1.el6.x86_64 #1 SMP Wed Jan 28 08:50:46 CET 2015 x86_64 x86_64 x86_64 GNU/Linux"/>
    <Info name="Dir" value="/home/joosep/btv/CMSSW_7_4_0/src/RecoBTag/CMSCSTagger"/>
    <Info name="Training events" value="1692351"/>
    <Info name="TrainingTime" value="7.82964582e+03"/>
    <Info name="AnalysisType" value="Classification"/>
    </GeneralInfo>
    <Options>
    <Option name="V" modified="Yes">False</Option>
    <Option name="VerbosityLevel" modified="Yes">Fatal</Option>
    <Option name="VarTransform" modified="No">None</Option>
    <Option name="H" modified="Yes">False</Option>
    <Option name="CreateMVAPdfs" modified="No">False</Option>
    <Option name="IgnoreNegWeightsInTraining" modified="No">False</Option>
    <Option name="NTrees" modified="Yes">{ntrees}</Option>
    <Option name="MaxDepth" modified="Yes">{maxdepth}</Option>
    <Option name="MinNodeSize" modified="No">5%</Option>
    <Option name="nCuts" modified="Yes">50</Option>
    <Option name="BoostType" modified="Yes">Grad</Option>
    <Option name="AdaBoostR2Loss" modified="No">quadratic</Option>
    <Option name="UseBaggedBoost" modified="Yes">False</Option>
    <Option name="Shrinkage" modified="Yes">{learnrate}</Option>
    <Option name="AdaBoostBeta" modified="No">5.000000e-01</Option>
    <Option name="UseRandomisedTrees" modified="No">False</Option>
    <Option name="UseNvars" modified="Yes">{usenvars}</Option>
    <Option name="UsePoissonNvars" modified="No">True</Option>
    <Option name="BaggedSampleFraction" modified="No">6.000000e-01</Option>
    <Option name="UseYesNoLeaf" modified="No">False</Option>
    <Option name="NegWeightTreatment" modified="No">ignorenegweightsintraining</Option>
    <Option name="Css" modified="No">1.000000e+00</Option>
    <Option name="Cts_sb" modified="No">1.000000e+00</Option>
    <Option name="Ctb_ss" modified="No">1.000000e+00</Option>
    <Option name="Cbb" modified="No">1.000000e+00</Option>
    <Option name="NodePurityLimit" modified="No">5.000000e-01</Option>
    <Option name="SeparationType" modified="No">giniindex</Option>
    <Option name="DoBoostMonitor" modified="Yes">False</Option>
    <Option name="UseFisherCuts" modified="No">False</Option>
    <Option name="MinLinCorrForFisher" modified="No">8.000000e-01</Option>
    <Option name="UseExclusiveVars" modified="No">False</Option>
    <Option name="DoPreselection" modified="No">False</Option>
    <Option name="SigToBkgFraction" modified="No">1.000000e+00</Option>
    <Option name="PruneMethod" modified="No">nopruning</Option>
    <Option name="PruneStrength" modified="No">0.000000e+00</Option>
    <Option name="PruningValFraction" modified="No">5.000000e-01</Option>
    <Option name="nEventsMin" modified="No">0</Option>
    <Option name="UseBaggedGrad" modified="No">False</Option>
    <Option name="GradBaggingFraction" modified="No">6.000000e-01</Option>
    <Option name="UseNTrainEvents" modified="No">0</Option>
    <Option name="NNodesMax" modified="No">0</Option>
    </Options>
    <Variables NVar="{nvars}">
    {varstring}
    </Variables>
    <Classes NClass="2">
    <Class Name="Signal" Index="0"/>
    <Class Name="Background" Index="1"/>
    </Classes>
    <Transformations NTransformations="0"/>
    <MVAPdfs/>
    <Weights NTrees="{ntrees}" AnalysisType="1">
    """.format(**{
            "mva_name": mva_name,
            "ntrees":cls.n_estimators,
            "maxdepth":cls.max_depth,
            "maxdepth":cls.max_depth,
            "usenvars":cls.max_features,
            "nvars": cls.n_features,
            "varstring": varstring,
            "learnrate": cls.learning_rate
            }
        )
    )
    for itree, t in enumerate(cls.estimators_[:, 0]):
        outfile.write('<BinaryTree type="DecisionTree" boostWeight="1.0" itree="{0}">\n'.format(itree, cls.learning_rate))
        recurse(cls, outfile, t.tree_)
        outfile.write('</BinaryTree>\n')
    outfile.write("""
      </Weights>
    </MethodSetup>
    """)
    outfile.close()

if __name__ == "__main__":
    from sklearn import datasets
    import pandas
    import math
    iris = datasets.load_iris()
    X = iris.data[:, :2]
    Y = iris.target == 0
    
    cols = ["a", "b"]
    data = pandas.DataFrame(X, columns=cols)
    cls = GradientBoostingRegressor(loss="huber", max_depth=4, n_estimators=100, verbose=True)
    cls.fit(X,Y)
    
    gbr_to_tmva(cls, data, "test.xml")

    import ROOT, array
    from ROOT import TMVA

    reader = TMVA.Reader("!V")
    vardict = {}
    for fn in cols:
        vardict[fn] = array.array("f", [0])
        reader.AddVariable(fn, vardict[fn])
    reader.BookMVA("testmva", "test.xml")
    
    def mva1(x,y):
        s = cls.decision_function([x,y])[0]
        return 2.0/(1.0+math.exp(-2.0*s))-1
        
    def mva2(x,y):
        vardict["a"][0] = x
        vardict["b"][0] = y
        return reader.EvaluateMVA("testmva")
    
    for i in range(X.shape[0]):
        x = X[i,0]
        y = X[i,1]
        z = Y[i]
        v1 = mva1(x,y)
        v2 = mva2(x,y)
        print x, y, z, v1, v2
