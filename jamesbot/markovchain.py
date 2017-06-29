import random

class MarkovChain:
    class Node:
        def __init__(self, word):
            self.word = word
            self.links = {}

        def add_link(self, node):
            if node in self.links:
                self.links[node] += 1
            else:
                self.links[node] = 1

        def next(self):
            return random.choices(list(self.links.keys()), self.links.values())[0]

        def __hash__(self):
            return hash(self.word)

    #source_material should be a list of lists of words.
    def __init__(self, sources=[]):
        self.root_node = self.Node(None)
        self.nodes = {}

        for source in sources:
            add_source(source)

    def add_source(self, source):
        prev = self.root_node

        for word in source:
            if word not in self.nodes:
                self.nodes[word] = self.Node(word)

            cur = self.nodes[word]
            prev.add_link(cur)
            prev = cur

        if prev != self.root_node:
            prev.add_link(None)

    def generator(self):
        node = self.root_node.next()

        while node != None:
            yield node.word
            node = node.next()

    def from_texts(texts):
        sources = []
        for text in texts:
            if not text:
                continue
            words = text.split(' ')
            sources.append(words)
        return MarkovChain(sources)
