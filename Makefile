all: testAutoTree
	
testAutoTree: test/TestAutoTree.cc
	$(CXX) src/AutoTree.cc test/TestAutoTree.cc `root-config --libs --cflags` -I./ -o testAutoTree

testHeaderGen: test/TestAutoTree.cc
	python/headergen.py interface/tree_template.hh interface/tree.hh python/branches.py
	$(CXX) test/TestTreeHeader.cc `root-config --libs --cflags` -I./ -o testTreeHeader

tmvaEvaluator: test/tmvaEvaluator.cc
	$(CXX) -g `root-config --cflags --libs` -lTMVA -I./ src/AutoTree.cc test/tmvaEvaluator.cc -o tmvaEvaluator	

TreeSelector: test/TreeSelector.cc
	$(CXX) -g `root-config --cflags --libs` -I./ src/AutoTree.cc test/TreeSelector.cc -o TreeSelector	
