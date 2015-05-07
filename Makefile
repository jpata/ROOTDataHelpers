all: testAutoTree
	
testAutoTree: test/TestAutoTree.cc
	$(CXX) src/AutoTree.cc test/TestAutoTree.cc `root-config --libs --cflags` -I./ -o testAutoTree
