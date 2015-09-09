import nltk
from gensim.models import word2vec
import json
import sys
from nltk import word_tokenize
import re
from stanford_corenlp_pywrapper import sockwrap
from ast import literal_eval
import operator
import time

'''
algo:
    start from parse tree:
    1. if you can find NP -> JJ, NN, parse JJ and NN. Look for NN as attribute.
    2. if you can find NP -> *, NN, NN, parse NN_1 and NN_2. Look for NN_1 and NN_2 as attributes.
    3. if you can find NP -> * , NN. Look for NN as attribute.
    4. PP -> TO, NN. This is location attribute most prob. So look for NN in Location.
    5. PP -> IN, NN. This could be either location or purpose. e.g. for honeymoon, from station.
    6. Make JJ indexable in elastic search.
'''

possibleNounTags = ['NN', 'NNP', 'NNS', 'NNPS']
possibleAdjTags = ['JJ', 'JJR', 'JJS', 'RB', 'RBS', 'RBR']
possibleVerbTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
model_file = "../word2vec-all/word2vec/trunk/vectors-phrase.bin"
stanford_jars = "/Volumes/anupam work/code/stanford-jars/3.5/*"
model = None
proc = None
exclude_noun = ["day", "hotel", "july", "ones", "years", "guest", "night", "year", "room"]

def loadModelFile():
    global model
    global model_file
    global proc
    model = word2vec.Word2Vec.load_word2vec_format(model_file, binary=True)
    proc = sockwrap.SockWrap("parse", corenlp_jars=[stanford_jars])

def find_lowest_subtree(tree, tag):
    if tree[0] == tag:
        print 'returning: ' + str(tree)
        return tree
    tree_len = len(tree)
    print 'tree: ' + str(tree)
    time.sleep(1)
    if tree == None or tree_len == 0:
        return None
    count = tree_len - 1
    final_val = None
    while count >= 0:
        print 'calling tree: ' + str(tree[count])
        val = find_lowest_subtree(tree[count], tag)
        if val != None:
            final_val = val
        count = count - 1
    return None

def find_lowest_subtree_2(tree, tag):
    if tree == None:
        return None
    tree_len = len(tree)
    if tree_len == 0:
        return None
    count = tree_len - 1
    print 'tree: ' + str(tree)
    while count >= 0:
        if type(tree[count]) == str:
            if tree[count] == tag:
                print 'returning: ' + str(tree)
                return tree
            else:
                count -= 1
                continue
        val = find_lowest_subtree_2(tree[count], tag)
        if val != None:
            return val
        count = count - 1
    return None

def find_subtree_2(tree, tag):
    if tree == None:
        return None
    tree_len = len(tree)
    if tree_len == 0:
        return None
    count = 0
    print 'tree: ' + str(tree)
    while count < tree_len:
        if type(tree[count]) == str:
            if tree[count] == tag:
                print 'returning: ' + str(tree)
                return tree
            else:
                count += 1
                continue
        val = find_subtree_2(tree[count], tag)
        if val != None:
            return val
        count = count + 1
    return None
        
def find_noun_array(processed):
    count = 0
    pos_count = len(processed['sentences'][0]['pos'])
    print 'pos: ' + str(processed['sentences'][0]['pos'])
    print 'tokens: ' + str(processed['sentences'][0]['tokens'])
    noun_arr = []
    while count < pos_count:
        if processed['sentences'][0]['pos'][count] in possibleNounTags:
            noun_arr.append(processed['sentences'][0]['tokens'][count])
        count = count + 1
    return noun_arr

def normalize(word):
    if word == None:
        return None
    return word.lower().replace(' ', '_').replace('-','_')

def is_present(word, map_val):
    if word in map_val:
        if map_val[word] == 1 or map_val[word] == 2:
            return True
    return False

def findExact(attribute_seed, word, word_val, path):
    if attribute_seed['next'] == {}:
        assert(word in attribute_seed['keywords'])
        assert(word_val == attribute_seed['keywords'][word])
        return
    else:
        for node in attribute_seed['next']:
#            if 'others' == node:
#                continue
            if word in attribute_seed['next'][node]['keywords'] and word_val == attribute_seed['next'][node]['keywords'][word]:
                path.append(node)
                findExact(attribute_seed['next'][node], word, word_val, path)
                break
        return

def is_any_noun_present(map_val, noun_arr):
    path = []
    for noun in noun_arr:
        noun = normalize(noun)
        if is_present(noun, map_val['keywords']):
            word_val = map_val['keywords'][noun]
            print 'found noun: ' + noun
            findExact(map_val, noun, word_val, path)
            break
    return path

def findBestDistance(keywords, word):
    winner_keyword = None
    max_distance = -1
    global model
    for key in keywords:
        if key == '' or key == None:
            continue
        val = keywords[key]
        if val == 1 or val == 2:
            key = normalize(key)
            try:
                local_distance = model.similarity(key, word)
            except KeyError:
                #print 'word2vec error: word not found: ' + key + ' ; ' + word
                continue
            if local_distance > max_distance:
                max_distance = local_distance
                winner_keyword = key
    return max_distance, winner_keyword

def findAndInsert(attribute_seed, word, path):
    #print 'word, path: ' + word + ' ; ' + str(path)
    if len(word) <= 2:
        return False
    max_distance = -1
    winner_node = None
    if attribute_seed['next'] == {}:
        #attribute_seed['keywords'][word] = 1
        return True
    for node in attribute_seed['next']:
        #print 'checking node: ' + node
        local_distance, local_keyword = findBestDistance(attribute_seed['next'][node]['keywords'], word)
        #print 'dist, keyword: ' + str(local_distance) + ' ; ' + str(local_keyword)
        if local_distance < 0.1:
            continue
        if local_distance > max_distance:
            max_distance = local_distance
            winner_node = node
    if winner_node == None:
        print 'winner node is none for: ' + word
        return False
    if winner_node == 'yoga':
        print 'yoga distance: ' + str(max_distance)
    path.append(winner_node)
    #attribute_seed['next'][winner_node]['keywords'][word] = 1
    return findAndInsert(attribute_seed['next'][winner_node], word, path)

def find_best_score(word, keywords_map):
    best_score = -1
    for key in keywords_map:
        try:
            score = model.similarity(word, key) * keywords_map[key]
        except KeyError:
            #print 'word2vec error: word not found: ' + word + ' ; ' + key
            continue
        if score > best_score:
            best_score = score
    return best_score

def find_score(data_map, map_val):
    score_sum = 0
    for key in data_map:
        if key in map_val['keywords'] and map_val['keywords'][key] >= 1:
            score_sum += 1 * data_map[key]
        else:
            best = find_best_score(key, map_val['keywords']) * data_map[key]
            if best > 0:
                score_sum += best
    return score_sum

def find_best_attribute_multi(noun_arr, map_val, path):
    if len(noun_arr) == 0:
        return None
    max_score = -1
    max_node = None
    for node in map_val['next']:
        score = find_score(noun_arr, map_val['next'][node])
        if score > max_score:
            print 'win: max_score, new_score: ' + str(max_score) + ' ; ' + str(score)
            max_score = score
            max_node = node
    assert(max_node != None)
    path.append(max_node)
    if len(map_val['next'][max_node]['next']) == 0:
        return
    else:
        find_best_attribute_multi(noun_arr, map_val['next'][max_node], path)
        
def find_best_attribute_multi_2(data_map, map_val, path):
    if len(data_map) == 0:
        return None
    max_score = -1
    max_node = None
    for node in map_val['next']:
        score = find_score(data_map, map_val['next'][node])
        if score > max_score:
            print 'win: max_score, new_score: ' + str(max_score) + ' ; ' + str(score) + ' ; ' + node
            max_score = score
            max_node = node
    assert(max_node != None)
    path.append(max_node)
    if len(map_val['next'][max_node]['next']) == 0:
        return
    else:
        find_best_attribute_multi_2(data_map, map_val['next'][max_node], path)

def find_best_attribute(noun_arr, map_val):
    if len(noun_arr) == 0:
        print 'Not Found: Subject and object are none and no noun present: ' + str(noun_arr)
        return []
    print 'noun arr: ' + str(noun_arr)
    path = is_any_noun_present(map_val, noun_arr)
    print '## noun: ' + str(path)
    if path == []:
        print 'No noun is present in tree. So finding best bet...'
        max_distance = -1
        winner_noun = None
        for noun in noun_arr:
            noun = normalize(noun)
            local_distance = findBestDistance(map_val['keywords'], noun)
            if local_distance > max_distance:
                max_distance = local_distance
                winner_noun = noun
        assert(winner_noun != None)
        path = []
        if findAndInsert(map_val, winner_noun, path):
            assert(path != [])
        else:
            print 'Unknown: Not able to insert line and noun: ' + str(noun_arr) + ' ; ' + winner_noun
    return path

def find_first_index(my_tuple, speech_list):
    count = 0
    while count < len(my_tuple):
        if my_tuple[count][0] in speech_list:
            return count
        count += 1
    return -1

def find_all(sub_tree, tags_list, nouns):
    tree_len = len(sub_tree)
    count = 0
    #print 'tree first: ' + str(sub_tree)
    while count < tree_len:
        if type(sub_tree[count]) == str:
            if sub_tree[count] in tags_list:
                nouns.append(sub_tree[count + 1])
                return
            else: 
                count = count + 1
                continue
        #print 'tree_next first: ' + str(sub_tree[count][0])
        if type(sub_tree[count]) == tuple:
            find_all(sub_tree[count], tags_list, nouns)
        count = count + 1
    return

def find_sub_obj(processed):
    deps = processed['sentences'][0]['deps_basic']
    subj_details = None
    obj_details = None
    mod_details = None
    for val in deps:
        if 'subj' in val[0]:
            subj_details = val
        if 'obj' in val[0]:
            obj_details = val
        if 'mod' in val[0]:
            mod_details = val
    #print 'details: ' + str(subj_details) + ' ; ' + str(obj_details) + ' ; ' + str(mod_details)
    #pos_tags = parsed_c['sentences'][0]['pos']
    tokens = processed['sentences'][0]['tokens']
    obj = None
    if obj_details == None:
        if mod_details != None:
            obj = tokens[mod_details[2]]
    else:
        obj = tokens[obj_details[2]]
    sub = None
    if subj_details is not None:
        sub = tokens[subj_details[2]]
    return sub, obj

def find_attribute_2(attribute_seed, user_input):
    processed = proc.parse_doc(user_input)
    if len(processed['sentences']) == 0:
        return None
    nouns = find_noun_array(processed)
    sub, obj = find_sub_obj(processed)
    data = {}
    for noun in nouns:
        n_noun = normalize(noun)
        if n_noun in data:
            data[n_noun] += 1
        else:
            data[n_noun] = 1
    if sub != None:
        if sub in possibleNounTags or sub in possibleAdjTags or sub in possibleVerbTags:
            n_sub = normalize(sub)
            if n_sub in data:
                data[n_sub] += 1.10
            else:
                data[n_sub] = 1.10
    if obj != None:
        if obj in possibleNounTags or sub in possibleAdjTags or sub in possibleVerbTags:
            n_obj = normalize(obj)
            if n_obj in data:
                data[n_obj] += 1.01
            else:
                data[n_obj] = 1.01
    print 'data: ' + str(data)
    path = []
    find_best_attribute_multi_2(data, attribute_seed['root'], path)
    print 'path: ' + str(path)
    return path

def find_attribute(attribute_seed, user_input):
    processed = proc.parse_doc(user_input)
    if len(processed['sentences']) == 0:
        return None
        
    parse_tree_str = str(processed['sentences'][0]['parse']).replace(' ', ' ,').replace(' ', '\' ').replace('(', '(\'').replace(')', '\')').replace(',', ',\'').replace('\'(', '(').replace(')\'', ')').replace(')\')', '))').replace(')\')', '))')

    print 'parse tree str: ' + str(parse_tree_str)
    parse_tree = literal_eval(parse_tree_str)
    print 'parse tree: ' + str(parse_tree)

    # find last PP or NP.
    path = []
    pp_tree = find_subtree_2(parse_tree, 'PP')
    if pp_tree == None:
        print 'NULL: pp_tree is null'
        np_tree = find_lowest_subtree_2(parse_tree, 'NP')
        if np_tree == None:
            print 'NULL: np_tree is null'
            noun_arr = []
            find_all(parse_tree, possibleNounTags + possibleAdjTags, noun_arr)
            find_best_attribute_multi(noun_arr, attribute_seed['root'], path)
        else:
            assert(np_tree[0] == 'NP')
            tree_len = len(np_tree)
            if np_tree[1][0] in possibleAdjTags and np_tree[2][0] in possibleNounTags:
                adj = np_tree[1][1]
                noun = np_tree[2][1]
                find_best_attribute_multi([adj, noun], attribute_seed['root'], path)
            else:
                #if np_tree[tree_len - 1][0] == 'NN':
                    # find all nouns:
                tree_count = 0
                noun_arr = []
                find_all(np_tree, possibleNounTags + possibleAdjTags, noun_arr)
                # off all the nouns find the nearest attribute.
                print 'noun arr: ' + str(noun_arr)
                find_best_attribute_multi(noun_arr, attribute_seed['root'], path)
    else:
        print 'pp_tree: ' + str(pp_tree)
        assert(pp_tree[0] == 'PP')
        # mostly location attribute.
        tree_len = len(pp_tree)
        noun_index = find_first_index(pp_tree, ['NP'])
        if noun_index == -1:
            print 'ERROR: No NP found in: ' + str(pp_tree)
        else: 
            noun_val_arr = []
            find_all(pp_tree[noun_index], possibleNounTags + possibleAdjTags, noun_val_arr)
            if pp_tree[1][0] == 'TO':
                #only location attribute.
                # find location target for noun_val
                find_best_attribute_multi(noun_val_arr, attribute_seed['root']['next']['location'], path)
            else:
                if pp_tree[1][0] == 'IN':
                    # either purpose or location.
                    # choose between purpose and location.
                    find_best_attribute_multi(noun_val_arr, attribute_seed['root'], path)
                    
    return path

if __name__ == "__main__":
    loadModelFile()
    attribute_seed = json.loads(open(sys.argv[1], 'r').read())
    user_input = raw_input("Some input please: ")
    while user_input != 'stop':
        user_input_modified = user_input.replace('/', ' ')
        path = find_attribute_2(attribute_seed, user_input_modified)
        print 'path found: ' + str(path)
        user_input = raw_input("Some input please: ")