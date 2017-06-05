import subprocess, sys
import yaml
from cassandra_yaml import document
import os

with open("cassandra.yaml", 'r') as stream:
	print "file opened"
	yaml_file = yaml.load(stream)

print "HI"
# a 50/50
# b 95 read/ 5 write
# c 100 read

res = {}
concurrent_reads  = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
concurrent_writes = [4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
for write_val in concurrent_writes:
	for read_val in concurrent_reads:
		yaml_file['concurrent_reads'] = read_val
		yaml_file['concurrent_writes'] = read_val
		# print yaml_file
		with open('cassandra.yaml', 'w') as outfile:
			print("J")
			yaml.dump(yaml_file, outfile, default_flow_style=False)

		
		"save cassandra file"
		p = subprocess.call("cp -r /scripts/cassandra.yaml /etc/cassandra", shell=True)
		# p.communicate()

		print "restart cassandra"
		command = ['/usr/sbin/service', 'cassandra', 'restart'];
		#shell=FALSE for sudo to work.
		subprocess.call(command, shell=False)

		print "run workloads"
		workloads = ["c"]
		for workload in workloads:
			read_val = "%s-%s" % (read_val, write_val)
			p = subprocess.call("rm -Rf %s/%s" % (workload, read_val), shell=True)
			p = subprocess.call("mkdir %s/%s" % (workload, read_val), shell=True)
			## how many runs to do
			for i in range(10):
				print i
				with open("%s/%s/%s-stdout.txt" % (workload, read_val, i),"wb") as out, open("%s/%s/%s-stderr.txt" % (workload, read_val, i),"wb") as err:
					p = subprocess.Popen("./ycsb-0.12.0/bin/ycsb run basic -P ycsb-0.12.0/workloads/workload%s" % workload, 
						shell=True, 
						stdout=out,
						stderr=err)
					p.communicate()

		
		for file in os.listdir("%s/%s/" % (workload, read_val)):

			if file.endswith("out.txt"):
				print "%s/%s/%s" % (workload, read_val, file)

				with open("%s/%s/%s" % (workload, read_val, file), 'r') as f:
					for line in f.readlines():
						if "[READ]" in line:

							l 	= line.split(', ')
							key = l[1]
							val = int(l[2].replace("\n", "").split(".")[0])

							if key not in res:
								res[key] = {}


							if read_val in res[key]:
								res[key][read_val].append(val)
							else:
								res[key][read_val] = [val]

		print res