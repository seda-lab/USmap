import sys
import os
from subprocess import Popen, PIPE
import shlex
import json

def run_louvain_standard(filename, num_its=100):
	execpath=os.getcwd() + "/gen-louvain/"

	convert_cmd = execpath  + "convert -i " + filename + " -o graph.bin -w graph.weights -r graph.labels";
	p = Popen( shlex.split(convert_cmd), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();

	run_command = execpath  + "louvain graph.bin -l -1 -q 0 -w graph.weights";
	best_mod = -1;

	for i in range(num_its):
	
		partition = open("tmp.tree", "w")
		p = Popen( shlex.split(run_command), stdout=partition, stderr=PIPE)
		stdout, stderr = p.communicate();
		mod = float(stderr.decode("utf-8").strip().split("\n")[-1].split()[0]);
		
		if mod > best_mod:
			best_mod = mod;
			os.system('cp tmp.tree graph.tree');
		
		print("Louvain iteration", i, "mod", mod, "best_mod", best_mod)
		partition.close();
	os.system('rm tmp.tree');
	
	hierarchy_command1 = execpath  + "hierarchy graph.tree -l -1";
	p = Popen( shlex.split(hierarchy_command1), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();
	level = stdout.decode("utf-8").strip().split("\n")[-1].split()[1].split(":")[0];
	
	hierarchy_command2 = execpath  + "hierarchy graph.tree -l " + level;
	p = Popen( shlex.split(hierarchy_command2), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();
	partition = {}
	for r in stdout.decode("utf-8").strip().split("\n"):
		w = r.split();
		partition[ w[0] ] = w[1];
	
	labels = {};
	with open("graph.labels", 'r') as infile:
		for line in infile:
			w = line.split();
			labels[w[1]] = w[0]
	
	labelled_partition = {};
	for k in partition:
		labelled_partition[ int(labels[k]) ] = int(partition[k]);

	return best_mod, labelled_partition;	
	
	
def run_louvain_null(filename, nullfilename, labelfile, num_its=100):
	execpath=os.getcwd() + "/gen-louvain/"
	
	convert_cmd1 = execpath  + "convert -i " + filename + " -o graph.bin -w graph.weights";
	p = Popen( shlex.split(convert_cmd1), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();
	
	convert_cmd2 = execpath  + "convert -i " + nullfilename + " -o null.bin -w null.weights";
	p = Popen( shlex.split(convert_cmd2), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();


	run_command = execpath  + "louvain graph.bin -l -1 -q 10 -w graph.weights -n null.bin -x null.weights";
	best_mod = -1;

	for i in range(num_its):
	
		partition = open("tmp.tree", "w")
		p = Popen( shlex.split(run_command), stdout=partition, stderr=PIPE)
		stdout, stderr = p.communicate();

		mod = float(stderr.decode("utf-8").strip().split("\n")[-1].split()[0]);

		if mod > best_mod:
			best_mod = mod;
			os.system('cp tmp.tree graph.tree');
		
		print("Louvain iteration", i, "mod", mod, "best_mod", best_mod)
		partition.close();
	os.system('rm tmp.tree');
	
	hierarchy_command1 = execpath  + "hierarchy graph.tree -l -1";
	p = Popen( shlex.split(hierarchy_command1), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();
	level = stdout.decode("utf-8").strip().split("\n")[-1].split()[1].split(":")[0];
	
	hierarchy_command2 = execpath  + "hierarchy graph.tree -l " + level;
	p = Popen( shlex.split(hierarchy_command2), stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate();
	
	partition = {}
	for r in stdout.decode("utf-8").strip().split("\n"):
		w = r.split();
		partition[ w[0] ] = w[1];
	
	with open(labelfile, 'r') as infile:
		for line in infile:
			labels = json.loads(line);
			
	labelled_partition = {};
	for k in partition:
		labelled_partition[ int(labels[str(k)]) ] = int(partition[k]);

	return best_mod, labelled_partition;	
	
	
