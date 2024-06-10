import itertools
import string
from ScriptureReference import ScriptureReference
import pprint
import time
import re

pp = pprint.PrettyPrinter(indent=4)

passages = ScriptureReference('gen 1:1', 'rev 22:21').verses

verses = [verse[1] for verse in passages]

j = 4
# verses = [
#     "In the beginning God created the heavens and the earth.",
#     "Now the earth was formless and empty, darkness was over the surface of the deep.",
#     "And the Spirit of God was hovering over the waters.",
#     # Add more verses as needed
# ]

# remove all punctuation from verses
verses = [re.sub(r'[^a-z0-9 ]', '', verse.lower()) for verse in verses]

verses = [verse for verse in verses if verse != '']

# [print(verse) for verse in verses]

seed_size = 1000
known_ngrams = []
seed_corpus = []

ngram_dict = {}
unique_ngrams = []

def get_ngrams(text, n):
    """Generate n-grams from a given text."""
    words = text.split()
    ngrams = list(itertools.chain(*[zip(*[words[i:] for i in range(j)]) for j in range(1, n+1)]))
    return [' '.join(ngram) for ngram in ngrams]

def find_unique_ngrams(verse, max_n):
    """Find unique n-grams up to the max_n order in the verse."""
    ngrams_set = set()
    for n in range(1, max_n + 1):
        ngrams_set.update(get_ngrams(verse, n))
    return list(ngrams_set)

# start time
start = time.time()

# get frequency count of all unique ngrams in corpus
# get all unique ngrams per verse
for i, verse in enumerate(verses):
    unique_verse_ngrams = find_unique_ngrams(verse, j)
    unique_ngrams.append(unique_verse_ngrams)
    for ngram in unique_verse_ngrams:
        if ngram not in ngram_dict:
            ngram_dict[ngram] = 1
        else:
            ngram_dict[ngram] += 1

# print("\nngram_dict")
# pp.pprint(ngram_dict)
# print("\nunique_ngrams")
# [print(unique_ngram_set) for unique_ngram_set in unique_ngrams]

# ngram_dict now has <unique_ngram: frequency_count> pairs 
# unique_ngrams now has list where elem i is list of unique ngrams for verse i 

# get sum of all ngram frequency counts for each verse
freq_count_sums = []
for i, verse in enumerate(verses):
    count = 0
    for ngram in unique_ngrams[i]:
        count += ngram_dict.get(ngram, 0)
    freq_count_sums.append(count / len(verse))

# print("\nfreq_count_sums")     
# [print(freq_count_sums[i]) for i in range(len(freq_count_sums))]

# freq_count_sums [i] will have total ngram frequency count for verse i

known_ngrams = []
score_data = []
seed_time_data = []
for i in range(seed_size):
    # print("\nseed loop entry ", i, "\n")
    # top_verse = verses[top_score_index]
    seed_start = time.time()
    top_score_dropped = False
    init_entry = True
    
    # find the real top score
    while top_score_dropped or init_entry:
        init_entry, top_score_dropped = False, False
        top_score_index = freq_count_sums.index(max(freq_count_sums))
        # print("\nwhile loop entry\ntop score index: ", top_score_index)
        # print("top scoring verse: ", verses[top_score_index])
        # print("score: ", freq_count_sums[top_score_index])
                
        # recalculate top score
        # for each unique ngram in the top-scoring verse
        for ngram in unique_ngrams[top_score_index]:
            if ngram in known_ngrams:
                # print(f"\nngram {ngram} in known_ngrams")
                freq_count_sums[top_score_index] -= ngram_dict.get(ngram, 0) / len(verses[top_score_index])
                while ngram in unique_ngrams[top_score_index]:
                    unique_ngrams[top_score_index].remove(ngram)
                top_score_dropped = True
        
        # print("score dropped to: ", freq_count_sums[top_score_index])

    seed_corpus.append(verses[top_score_index])
    score_data.append(freq_count_sums[top_score_index])
    freq_count_sums[top_score_index] = 0
    known_ngrams += (unique_ngrams[top_score_index])
    seed_end = time.time()
    seed_time_data.append(seed_end - seed_start)
    # print percentage completion
    print(f"\r{i/seed_size*100:.2f}%", end="")

# end time
end = time.time()

# print("\nknown_ngrams:")
# [print(known_ngram) for known_ngram in known_ngrams]
[print(verse) for verse in seed_corpus]

# print total time taken
print("\nTime taken: ", end - start)

# plot the scores
import matplotlib.pyplot as plt
plt.plot(score_data)
plt.ylabel('Score')
plt.xlabel('Seed')
plt.show()

# plot the time taken per seed
plt.plot(seed_time_data)
plt.ylabel('Time taken')
plt.xlabel('Seed')
plt.show()
