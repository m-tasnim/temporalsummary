from rdflib import Graph, URIRef, Literal
from random import sample
import numpy as np
from concepts import Context

class TemporalSummary:
    """
    TODO: Describe what this class does
    """
    # sample graphs_path => "data/{}/persondata_en_10.ttl".format(year)
    def __init__(self, subjects_path, graphs_paths):
        self.graphs = []
        self.subjects = []
        self.triples = 0
        self.summarized_triples = 0
        with open(subjects_path) as fp:
            for line in fp:
                self.subjects.append(line.strip())
        for graph_path in graphs_paths:
            graph = Graph()
            graph.parse(graph_path, format='turtle')
            self.triples += sum(1 for x in graph.triples((None, None, None)))
            self.graphs.append(graph)

    def summarize(self):
        for subject in self.subjects:
            molecules = self.get_molecules(subject)
            fca_result = self.local_fca(molecules)
            summary = self.fca_summarization(fca_result)
            self.summarized_triples += len(summary)
            # for (mlist, plist) in summary:
            #     print(mlist, plist)

        print("Original triples: {}".format(self.triples) )
        print("Summarized triples: {}".format(self.summarized_triples))
        print("Compression: {}".format(self.triples - self.summarized_triples))

    def fca_summarization(self, fca_result):
        summary = []
        intents = [plist for (mlist, plist) in fca_result]
        sorted_intents = lists = [i for i, _ in (sorted(enumerate(intents), key=lambda x: len(x[1])))]

        for index in sorted_intents:
            mlist, plist = fca_result[index]
            if len(mlist) > 0 and len(plist) > 0:
                summary.append((mlist, plist))
            if len(mlist) > 1:
                for i in range(len(fca_result)):
                    x, y = fca_result[i]
                    if i != index:
                        fca_result[i] = (x, list(set(y) - set(plist)))
        return summary

    def get_molecules(self, subject):
        molecules = []
        for graph in self.graphs:
            molecule = Graph()
            molecule += graph.triples((URIRef(subject), None, None))
            molecules.append(molecule)
        return molecules

    def get_properties(self, molecules):
        properties = []
        for molecule in molecules:
            for (s, p, o) in molecule:
                properties.append((p, o))
        return list(set(properties))

    def local_fca(self, molecules):
        props = self.get_properties(molecules)
        props = list(set(props))
        sub = list(molecules[0].subjects())[0]

        molecule_properties = [str(prop.encode('utf-8')) + '->' + str(value.encode('utf-8')) for prop, value in props]
        molecule_names = ["{}_{}".format(str(sub.encode('utf-8')), y) for y in [2014, 2015, 2016]]

        mat = []
        for molecule in molecules:
            row = [False] * len(props)
            for idx, (prop, val) in enumerate(props):
                if (sub, prop, val) in molecule:
                    row[idx] = True
            mat.append(row)

        c = Context(molecule_names, molecule_properties, mat)
        res = c.lattice
        result = []
        for (extent, intent) in res:
            result.append((list(extent), list(intent)))

        return result


graphs_paths = ["data/shortened/person{}_10.nt".format(year) for year in [2014, 2015, 2016]]
summarization = TemporalSummary("data/subjects.txt", graphs_paths)
summarization.summarize()


