import sys, os
from collections import Counter
from math import log, exp
from string import punctuation
from operator import mul

candidate_path = sys.argv[1]
reference_path = sys.argv[2]
reference_files = []




if os.path.isfile(reference_path):
	reference_files = [reference_path]
else:
	reference_files = [os.path.join(reference_path, f) for f in os.listdir(reference_path) if os.path.isfile(os.path.join(reference_path, f))]

print reference_files

def read_file(fpath):
	with open(fpath) as f:
		content = f.readlines()
	#return [x.strip().lower().translate(None, punctuation).split() for x in content]
	return [x.strip().lower().split() for x in content]

references = []
candidates = read_file(candidate_path)
len_candidates = []

ngram_candidates = []
	
def ngram_counter(sentence):
	return {
		1: dict(Counter(sentence).most_common()),
		2: dict(Counter([' '.join(sentence[i:i+2]) for i in xrange(len(sentence)-1)]).most_common()),
		3: dict(Counter([' '.join(sentence[i:i+3]) for i in xrange(len(sentence)-2)]).most_common()),
		4: dict(Counter([' '.join(sentence[i:i+4]) for i in xrange(len(sentence)-3)]).most_common()),
	}

for s in candidates:
	len_candidates.append(len(s))
	ngram_candidates.append(ngram_counter(s))


"""
Example

ngram_candidates = [{
	1: {<uniword>: <uniword-count>,...},
	2: {<biword>: <biword-count>,...},
	..
	..
	4: ...
},{...},{...}]

ngram_references = [
{
	1: {<uniword>: <best-uniword-count>,...},
	2: {<biword>: <biword-count>,...},
	..
	..
	4: ...
},{...}]

"""

ngram_references = []
len_references = []

for r in reference_files:
	with open(r) as f:
		content = f.readlines()
	#temp = [[x.strip().lower().translate(None, punctuation).split()] for x in content]
	temp = [[x.strip().lower().split()] for x in content]
	ngram_temp = [ngram_counter(x[0]) for x in temp]
	len_temp = [len(x[0]) for x in temp]
	if references:
		for i in xrange(len(references)):
			references[i] += temp[i]
			ngram_references[i][1].update({k:max(ngram_references[i][1].get(k,-1),ngram_temp[i][1][k]) for k in ngram_temp[i][1]})
			ngram_references[i][2].update({k:max(ngram_references[i][2].get(k,-1),ngram_temp[i][2][k]) for k in ngram_temp[i][2]})
			ngram_references[i][3].update({k:max(ngram_references[i][3].get(k,-1),ngram_temp[i][3][k]) for k in ngram_temp[i][3]})
			ngram_references[i][4].update({k:max(ngram_references[i][4].get(k,-1),ngram_temp[i][4][k]) for k in ngram_temp[i][4]})
			#ngram_references[i] += ngram_temp[i]

			len_references[i] = len_temp[i] if abs(len_temp[i] - len_candidates[i]) < abs(len_references[i] - len_candidates[i]) else len_references[i]

	else:
		references = temp
		ngram_references = ngram_temp
		len_references = len_temp

def calculate_precision_score(candidate, reference):
	#print total
	total = sum(candidate.values())
	num = 0.0
	for w in candidate:
		if w in reference:
			num += min(candidate[w],reference[w])
	#print total, num
	try:
		return num,total 
	except ValueError:
		return 0,total
	except ZeroDivisionError:
		return 0,total

c = sum(len_candidates)
r = sum(len_references)

def brevity_penalty(c,r):
    if c > r:
        bp = 1
    else:
        bp = exp(1-(float(r)/c))
    return bp

def geometric_mean(precisions):
    return (reduce(mul, precisions)) ** (1.0 / len(precisions))

precisions = []
p = 0
p_total = 0

"""
ngram_candidates[1][1] = {'the' : 17, 'as': 10}
len_candidates[1] = 17
ngram_references[1][1] = {'the': 2,'as':2}

left = calculate_precision_score(4,len_candidates[1], ngram_candidates[1][4], ngram_references[1][4])
print left
"""
for j in xrange(1,5):
	p = 0
	p_total = 0
	for i in xrange(len(ngram_candidates)):
		#print ngram_candidates[i][j]
		#print ngram_references[i][j]
		temp,temp_t  = calculate_precision_score(ngram_candidates[i][j], ngram_references[i][j])
		p += temp
		p_total += temp_t

	precisions.append(p/p_total)

bleu = geometric_mean(precisions) * brevity_penalty(c,r)

out = open('bleu_out.txt', 'w')
out.write(str(bleu))
out.close()
