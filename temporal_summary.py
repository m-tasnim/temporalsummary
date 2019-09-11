from rdflib import Graph, URIRef, Literal
from random import sample
from concepts import Context

class TemporalSummary:
    """
    TODO: Describe what this class does
    """
    # sample graphs_path => "data/{}/persondata_en_10.ttl".format(year)
    def __init__(self, subjects_path, graphs_paths):
        self.graphs = []
        self.subjects = []
        with open(subjects_path) as fp:
            self.subjects.append(fp.readline().strip())
        for graph_path in graphs_paths:
            graph = Graph()
            graph.parse(graph_path, format='turtle')
            self.graphs.append(graph)

    def summarize(self):
        for subject in self.subjects:
            molecules = self.get_molecules(subject)
            fca_result = self.local_fca(molecules)
            summary = self.fca_summarization(fca_result)
            for ((mlist, plist)) in summary:
                print(mlist, plist)
                # print("extent:{}\nintent:{}".format(extent, intent))

    def fca_summarization(self, fca_result):
        summary = []
        for mlist, plist in fca_result:
            if len(mlist) > 1 and len(plist) >=0:
                summary.append((mlist, plist))
                fca_result.remove((mlist, plist))
        for mlist, plist in fca_result:
            if len(mlist) == 1 and len(plist) >=0:
                for (x, y) in summary:
                    if mlist[0] in x and y in plist:
                        plist.remove(y)
                if len(plist) >= 0:
                    summary.append((mlist, plist))
        return summary

    def get_molecules(self, subject):
        molecules = []
        for graph in self.graphs:
            molecule = Graph()
            molecule += graph.triples((URIRef(subject), None, None))
            molecules.append(molecule)
        # for molecule in molecules:
        #     print("molecule:\n")
        #     for s, p, o in molecule:
        #         print ("<{}><{}><{}>\n".format(s, p, o))
        return molecules

    def get_properties(self, molecules):
        properties = []
        for molecule in molecules:
            for (s, p, o) in molecule:
                properties.append((p, o))
        return list(set(properties))

    def local_fca(self, molecules):
        props = self.get_properties(molecules)
        sub = list(molecules[0].subjects())[0]

        molecule_properties = [str(prop) + '->' + str(value) for prop, value in props]
        molecule_names = ["{}_{}".format(str(sub), y) for y in [2014, 2015, 2016]]

        mat = []
        for molecule in molecules:
            row = [False] * len(props)
            for idx, (prop, val) in enumerate(props):
                if (sub, prop, val) in molecule:
                    row[idx] = True
            mat.append(row)

        print(molecule_names)
        print(molecule_properties)
        print(mat)
        c = Context(molecule_names, molecule_properties, mat)
        res = c.lattice
        result = []
        for (extent, intent) in res:
            result.append((list(extent), list(intent)))

        return result


graphs_paths = ["data/shortened/person{}_10_test.nt".format(year) for year in [2014, 2015, 2016]]
summarization = TemporalSummary("data/subjects_test.txt", graphs_paths)
summarization.summarize()


