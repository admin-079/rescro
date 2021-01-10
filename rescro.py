#!/usr/bin/python3

import optparse
import sys
import concurrent.futures
import re
import requests
import yaml

BLUE='\033[94m'
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CLEAR='\x1b[0m'

print(BLUE + "Rescro[1.0] by ARPSyndicate" + CLEAR)
print(YELLOW + "regular expression extractor for webpages" + CLEAR)

if len(sys.argv)<2:
	print(RED + "[!] ./rescro --help" + CLEAR)
	sys.exit()

else:
    parser = optparse.OptionParser()
    parser.add_option('-l', '--list', action="store", dest="list", help="list of urls to scrape")
    parser.add_option('-s', '--signatures', action="store", dest="sigs", help="signatures to be used", default="signatures.yaml")
    parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="enable logging", default=False)
    parser.add_option('-T', '--threads', action="store", dest="threads", help="threads", default=20)
    parser.add_option('-o', '--output', action="store", dest="output", help="output results")    

inputs, args = parser.parse_args()
if not inputs.list:
	parser.error(RED + "[!] list of targets not given" + CLEAR)
sigs = str(inputs.sigs)
verbose = inputs.verbose
output = str(inputs.output)
threads = int(inputs.threads)
result = []

with open(str(inputs.list)) as f:
	targets=f.read().splitlines()

try:
	with open(sigs, encoding='utf-8') as signatures:
		sig = yaml.load(signatures, Loader=yaml.FullLoader)
except:
    print(RED + "[!] invalid signatures database" + CLEAR)
    sys.exit()

def getResults(target):
    if verbose:
        print(YELLOW + "[*] "+target)
    response = requests.get(target).text
    for regex in sig.keys():
        for reg in sig[regex]:
            match = re.finditer(reg, response, re.I)
            matches= list(set([x.group() for x in match]))
            matches.sort()
            if len(matches)>0:
                for data in matches:
                    print(BLUE + "[{0}] [{2}] {1}".format(regex, data, target) + CLEAR)
                    result.append("[{0}] [{2}] {1}".format(regex, data, target)) 

with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    try:
        executor.map(getResults, targets)
    except(KeyboardInterrupt, SystemExit):
        print(RED + "[!] interrupted" + CLEAR)
        executor.shutdown(wait=False)
        sys.exit()
if inputs.output:
    result = list(set(result))
    result.sort()
    with open(output, 'w') as f:
        f.writelines("%s\n" % line for line in result)

print(YELLOW+"[*] done"+CLEAR)