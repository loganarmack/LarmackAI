from math import floor
from os import path
import substr.constant as const
import json

def load_words():
    file_path = path.abspath(__file__)
    dir_path = path.dirname(file_path)
    word_path = path.join(dir_path, "words_alpha.txt")
    with open(word_path, 'r') as word_file:
        valid_words = set(word_file.read().split())
    
    return valid_words

def get_sorted_sets():
    word_list = load_words()
    two_sets = {}
    three_sets = {}

    # Counts frequency of each 2- and 3-length substring
    for word in word_list:
        for i in range(len(word) - 1):
            # gets lowercase substring of length 2
            pair = word.lower()[i : i + 2]

            if not pair in two_sets:
                two_sets[pair] = [1, [word.lower()]]
            else:
                two_sets[pair][0] += 1
                two_sets[pair][1].append(word.lower())

            # must be at least 3 characters left in string
            if i + 2 < len(word):
                # gets lowercase substring of length 3
                triple = word.lower()[i : i + 3]

                if not triple in three_sets:
                    three_sets[triple] = [1, [word.lower()]]
                else:
                    three_sets[triple][0] += 1
                    three_sets[triple][1].append(word.lower())

    # Remove all entries less than MIN_WORDS:
    trimmed_two_set = {k: v for k, v in two_sets.items() if v[0] > const.MIN_WORDS}
    trimmed_three_set = {k: v for k, v in three_sets.items() if v[0] > const.MIN_WORDS}

    sorted_two = {
        k: v for k, v in sorted(trimmed_two_set.items(), reverse=True, key=lambda item: item[1][0])
    }
    sorted_three = {
        k: v for k, v in sorted(trimmed_three_set.items(), reverse=True, key=lambda item: item[1][0])
    }

    return sorted_two, sorted_three

# export the list of substring frequencies to a csv
def export_frequencies(two_set, three_set):
    two_file = open("two_pairs.csv", "w")
    three_file = open("three_pair.csv", "w")

    two_file.write("Pair, Occurances\n")
    three_file.write("Triplet, Occurances\n")

    for pair in two_set:
        two_file.write("%s, %d\n" % (pair, two_set[pair][0]))

    for triplet in three_set:
        three_file.write("%s, %d\n" % (triplet, three_set[triplet][0]))

    two_file.close()
    three_file.close()


# break down a set of substrings into separate levels based on frequency
def get_levels(substr_set, num_levels):
    # initialize levels to be list of 5 empty lists
    levels = [{} for _ in range(num_levels)]

    # set cutoffs at certain percentage threshholds number of levels
    # 50%, 25%, 12.5%, etc.
    cutoffs = [floor(len(substr_set) / (2 ** (i + 1))) for i in range(num_levels - 1)]
    cutoffs.reverse()

    curr_level = 0
    for i, substr in enumerate(substr_set):
        if curr_level < len(cutoffs) and i > cutoffs[curr_level]:
            curr_level += 1
        levels[curr_level][substr] = substr_set[substr][1]

    return levels


# exports the different levels into a json so it doesn't need to be
# recalculated each time
def export_levels(num_levels):
    pair_levels = get_pair_levels(num_levels)
    triplet_levels = get_triplet_levels(num_levels)

    level_pair = {2: pair_levels, 3: triplet_levels}

    with open("levels.json", "w") as f:
        f.write(json.dumps(level_pair))


def get_pair_levels(num_levels):
    sorted_two, _ = get_sorted_sets()
    return get_levels(sorted_two, num_levels)


def get_triplet_levels(num_levels):
    _, sorted_three = get_sorted_sets()
    return get_levels(sorted_three, num_levels)


#export_levels(const.LEVELS)
