import sys

SH = 0; RE = 1; RA = 2; LA = 3

labels = ["nsubj", "csubj", "nsubjpass", "csubjpass", "dobj", "iobj", "ccomp", "xcomp", "nmod", "advcl", "advmod", "neg", "aux", "auxpass", "cop", "mark", "discourse", "vocative", "expl", "nummod", "acl", "amod", "appos", "det", "case", "compound", "mwe", "goeswith", "name", "foreign", "conj", "cc", "punct", "list", "parataxis", "remnant", "dislocated", "reparandum", "root", "dep", "nmod:npmod", "nmod:tmod", "nmod:poss", "acl:relcl", "cc:preconj", "compound:prt"]

def read_sentences():
    sentence = []
    sentences = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            if sentence:
                sentences.append(sentence)
                sentence = []
        elif line[0] != "#":
            token = line.split() 
            if len(token) >= 4: 
                sentence.append(token)
    if sentence: sentences.append(sentence)
    return sentences

def attach_orphans(arcs, n):
    attached = []
    for (h, d, l) in arcs:
        attached.append(d)
    for i in range(1, n):
        if not i in attached:
            arcs.append((0, i, "root"))

def print_tab(arcs, words, tags):
    hs = {}
    ls = {}
    for (h, d, l) in arcs:
        hs[d] = h
        ls[d] = l
    for i in range(1, len(words)):
        print("\t".join([words[i], tags[i], str(hs[i]), ls[i]]))
    print()
        
def print_tree(root, arcs, words, indent):
    if root == 0:
        print(" ".join(words[1:]))
    children = [(root, i, l) for i in range(len(words)) for l in labels if (root, i, l) in arcs]
    for (h, d, l) in sorted(children):
        print(indent + l + "(" + words[h] + "_" + str(h) + ", " + words[d] + "_" + str(d) + ")")
        print_tree(d, arcs, words, indent + "  ")

def transition(trans, stack, buffer, arcs):
    action, label = trans
    
    if action == SH:
        stack.insert(0, buffer.pop(0))
        
    elif action == RE:
        stack.pop(0)
        
    elif action == RA:
        arcs.append((stack[0], buffer[0], label))
        stack.insert(0, buffer.pop(0))
        
    elif action == LA:
        arcs.append((buffer[0], stack[0], label))
        stack.pop(0)
        
    return stack, buffer, arcs

def oracle(stack, buffer, heads, labels, arcs):
    if not stack: 
        return (SH, "_")
    
    top = stack[0]
    next_word = buffer[0]
    
    if heads[top] == next_word:
        return (LA, labels[top])
    
    elif heads[next_word] == top:
        return (RA, labels[next_word])
    
    elif has_head(top, arcs) and all_dependents_found(top, buffer, heads):
        return (RE, "_")
    
    else:
        return (SH, "_")

# helper fuctions
def has_head(node, arcs):
    return any(d == node for (h, d, l) in arcs)

def all_dependents_found(node, buffer, heads):
    for b_word in buffer:
        if heads[b_word] == node:
            return False
    return True


def parse(sentence):
    sentence.insert(0, ("0", "root", "_", "root", "_", "_", "0", "_"))
    
    words = [s[1] for s in sentence]
    tags = [s[3] for s in sentence]
    
    try:
        heads = [int(s[6]) for s in sentence]
        labels = [s[7] for s in sentence]
    except (ValueError, IndexError):
        heads = [int(s[2]) if len(s) > 2 else 0 for s in sentence]
        labels = [s[3] if len(s) > 3 else "_" for s in sentence]

    stack = [0]
    buffer = [x for x in range(1, len(words))]
    arcs = []
    
    while buffer:
        trans = oracle(stack, buffer, heads, labels, arcs)
        stack, buffer, arcs = transition(trans, stack, buffer, arcs)
        
    attach_orphans(arcs, len(words))
    if tab_format:
        print_tab(arcs, words, tags)
    else:
        print_tree(0, arcs, words, "")

if __name__ == "__main__":
    tab_format = False
    if len(sys.argv) == 2 and sys.argv[1] == "tab":
        tab_format = True
    for sentence in read_sentences():
        parse(sentence)
