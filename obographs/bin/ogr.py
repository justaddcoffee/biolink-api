#!/usr/bin/env python

"""
Command line wrapper to obographs library.

Type:

    ogr -h

For instructions

"""

import argparse
import networkx as nx
from networkx.algorithms.dag import ancestors, descendants
from obographs.ontol_factory import OntologyFactory
from obographs.graph_io import GraphRenderer
from obographs.slimmer import get_minimal_subgraph
import logging

def main():
    """
    Wrapper for OGR
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("Welcome!")
    parser = argparse.ArgumentParser(description='Wrapper for obographs library'
                                                 """
                                                 By default, ontologies are cached locally and synced from a remote sparql endpoint
                                                 """,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--resource', type=str, required=False,
                        help='Name of ontology')
    parser.add_argument('-o', '--outfile', type=str, required=False,
                        help='Path to output file')
    parser.add_argument('-t', '--to', type=str, required=False,
                        help='Output to (tree, dot, ...)')
    parser.add_argument('-d', '--direction', type=str, default='u', required=False,
                        help='u = up, d = down, ud = up and down')
    parser.add_argument('-p', '--properties', nargs='*', type=str, required=False,
                        help='Properties')
    parser.add_argument('-s', '--search', type=str, default='', required=False,
                        help='Search type. p=partial, r=regex')
    parser.add_argument('-S', '--slim', type=str, default='', required=False,
                        help='Slim type. m=minimal')
    parser.add_argument('-c', '--container_properties', nargs='*', type=str, required=False,
                        help='Properties to nest in graph')

    parser.add_argument('ids',nargs='*')

    args = parser.parse_args()
    handle = args.resource
    
    factory = OntologyFactory()
    ont = factory.create(handle)
    g = ont.get_filtered_graph(relations=args.properties)

    qids = []
    nodes = set()
    dirn = args.direction
    searchp = args.search
    for id in ont.resolve_names(args.ids,
                                is_remote = searchp.find('x') > -1,
                                is_partial_match = searchp.find('p') > -1,
                                is_regex = searchp.find('r') > -1):
        qids.append(id)
        nodes.add(id)
        # NOTE: we use direct networkx methods as we have already extracted
        # the subgraph we want
        if dirn.find("u") > -1:
            nodes.update(nx.ancestors(g, id))
        if dirn.find("d") > -1:
            nodes.update(nx.descendants(g, id))
    show_subgraph(g, nodes, qids, args)


def cmd_cycles(handle, args):
    g = retrieve_filtered_graph(handle, args)

    cycles = nx.simple_cycles(g)
    print(list(cycles))
    
def cmd_search(handle, args):
    for t in args.terms:
        results = search(handle, t)
        for r in results:
            print(r)

def show_subgraph(g, nodes, query_ids, args):
    """
    Writes graph
    """
    if args.slim.find('m') > -1:
        logging.info("SLIMMING")
        g = get_minimal_subgraph(g, query_ids)
    w = GraphRenderer.create(args.to)
    if args.outfile is not None:
        w.outfile = args.outfile
    w.write_subgraph(g, nodes, query_ids=query_ids, container_predicates=args.container_properties)
            
def resolve_ids(ont, ids, args):
    r_ids = []
    for id in ids:
        if len(id.split(":")) ==2:
            r_ids.append(id)
        else:
            matches = [n for n in g.nodes() if g.node[n].get('label') == id]
            r_ids += matches
    return r_ids

    
if __name__ == "__main__":
    main()
