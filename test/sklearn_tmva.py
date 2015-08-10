import sys
sys.path.append("/Users/joosep/Documents/ROOTDataHelpers/python/")
import sklearn_to_tmva
import sklearn
from sklearn import datasets
from sklearn.ensemble import GradientBoostingClassifier
import pandas
import math
import numpy as np
import matplotlib.pyplot as plt

data = pandas.read_csv("/Users/joosep/Desktop/data.csv")

data = data[data.eval("(Jet_CSV>=0) & (Jet_CSV<=1) & (Jet_CSVIVF>=0) & (Jet_CSVIVF<=1)")]
data = data[["Jet_CSV", "Jet_CSVIVF", "Jet_pt", "Jet_flavour"]]
data["mva1"] = 0.0
data["mva2"] = 0.0

cls = GradientBoostingClassifier(
    max_depth=4,
    learning_rate=0.01,
    n_estimators=100,
    verbose=True,
    min_samples_leaf=10,
    min_samples_split=10
)

cls.fit(
    np.array(data[["Jet_CSV", "Jet_CSVIVF", "Jet_pt"]]),
    np.array(np.abs(data[["Jet_flavour"]]) == 5).ravel(len(data), )
)

sklearn_to_tmva.gbr_to_tmva(
    cls,
    data[["Jet_CSV", "Jet_CSVIVF", "Jet_pt"]],
    "test.xml",
    coef=2
)

import ROOT, array
from ROOT import TMVA

reader = TMVA.Reader("!V")
vardict = {}
for fn in ["Jet_CSV", "Jet_CSVIVF", "Jet_pt"]:
    vardict[fn] = array.array("f", [0])
    reader.AddVariable(fn, vardict[fn])
reader.BookMVA("testmva", "test.xml")

def mva1(x,y,z):
    ret = 0
    for t in cls.estimators_[:,0]:
        r = t.tree_.predict(np.array([[x,y,z]], dtype="float32")) / cls.n_estimators * 2
        ret += r[0,0]
    return 2.0/(1.0+np.exp(-2.0*ret))-1

def mva2(x,y,z):
    vardict["Jet_CSV"][0] = x
    vardict["Jet_CSVIVF"][0] = y
    vardict["Jet_pt"][0] = z
    return reader.EvaluateMVA("testmva")

for i in range(len(data)):
    x = data.ix[i,"Jet_CSV"]
    y = data.ix[i,"Jet_CSVIVF"]
    z = data.ix[i,"Jet_pt"]
    v1 = mva1(x,y,z)
    v2 = mva2(x,y,z)
    data.ix[i, "mva1"] = v1
    data.ix[i, "mva2"] = v2

plt.scatter(data["mva1"], data["mva2"], alpha=0.5)
plt.xlim(-1,1)
plt.ylim(-1,1)

r1 = sklearn.metrics.roc_curve(np.abs(data["Jet_flavour"])==5, data["mva1"])
r2 = sklearn.metrics.roc_curve(np.abs(data["Jet_flavour"])==5, data["mva2"])

plt.figure(figsize=(5,5))
plt.plot(r1[1], r1[0], label="sklearn")
plt.plot(r2[1], r2[0], label="TMVA")
plt.grid()
plt.legend(loc=2)
plt.savefig("roc.pdf")

z = np.abs(data["mva1"] - data["mva2"])

print np.max(z)

