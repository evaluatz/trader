import subprocess


processes = []

schemas = [1, 3]

for i in schemas:
    processExec = ["/usr/bin/python3", "/root/00-Projects/trader/rebalance.py", "-s", str(i)]
    p = subprocess.Popen(processExec)
    processes.append(p)


for p in processes:
    p.wait()