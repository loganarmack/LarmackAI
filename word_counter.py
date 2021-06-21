from nltk.corpus import words
from math import floor

word_list =  words.words()
two_sets = {}
three_sets = {}

for word in word_list:
    for i in range(len(word) - 1):
        pair = word.lower()[i:i+2]
        if not pair in two_sets:
            two_sets[pair] = 1
        else:
            two_sets[pair] += 1

        if i + 2 < len(word):
            triple = word.lower()[i:i+3]
            if not triple in three_sets:
                three_sets[triple] = 1
            else:
                three_sets[triple] += 1

sorted_two = {k: v for k, v in sorted(two_sets.items(), reverse=True, key=lambda item: item[1])}
sorted_three = {k: v for k, v in sorted(three_sets.items(), reverse=True, key=lambda item: item[1])}

def export_frequencies(two_set, three_set):
    two_file = open("two_pairs.csv", "w")
    three_file = open("three_pair.csv", "w")

    two_file.write("Pair, Occurances\n")
    three_file.write("Triplet, Occurances\n")

    for pair in two_set:
        two_file.write("%s, %d\n" % (pair, two_set[pair]))

    for triplet in three_set:
        three_file.write("%s, %d\n" % (triplet, three_set[triplet]))

    two_file.close()
    three_file.close()

def get_levels(substr_set, num_levels):
    levels = [[] for _ in range(num_levels)]
    
    """  cutoff = len(substr_set) / num_levels

    for i, substr in enumerate(substr_set):
        levels[floor(i / cutoff)].append(substr) """

    cutoffs = [floor(len(substr_set)  / (2 ** (i + 1))) for i in range(num_levels - 1)]
    cutoffs.reverse()

    curr_level = 0
    for i, substr in enumerate(substr_set):
        if curr_level < len(cutoffs) and i > cutoffs[curr_level]:
            curr_level += 1
        levels[curr_level].append(substr)

    return levels

def export_levels(two_set, three_set, pair_levels, triplet_levels):
    pair_levels = get_levels(two_set)
    triplet_levels = get_levels(three_set)

    level_file = open("levels.csv", "w")

    lines = ["2-1, 2-2, 2-3, 2-4, 2-5, 3-1, 3-2, 3-3, 3-4, 3-5"]
    for level in pair_levels:
        for i, pair in enumerate(level):
            if len(lines) <= i + 1:
                lines.append("%s, " % (pair))
            else:
                lines[i + 1] += ("%s, " % (pair))

    for level in triplet_levels:
        for i, triplet in enumerate(level):
            if len(lines) <= i + 1:
                lines.append((" , , , , , %s, " % (triplet)))
            else:
                lines[i + 1] += ("%s, " % (triplet))
        

    for line in lines:
        level_file.write(line + "\n")

    level_file.close()

def get_pair_levels(num_levels):
    return get_levels(sorted_two, num_levels)

def get_triplet_levels(num_levels):
    return get_levels(sorted_three, num_levels)

def get_combined_levels(num_levels):
    pair_levels = get_levels(sorted_two, num_levels)
    triplet_levels = get_levels(sorted_three, num_levels)
    return [pair_levels[i] + triplet_levels[i] for i in range(num_levels)]
