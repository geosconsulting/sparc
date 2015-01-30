__author__ = 'fabio.lana'
import networkx as nx
import matplotlib.pyplot as plt

g = nx.DiGraph()
g.add_edge('a','b',weight=0.1)
g.add_edge('b','c',weight=1.5)
g.add_edge('a','c',weight=1.0)
g.add_edge('c','d',weight=2.2)
g.add_edge('d','e',weight=2.2)
g.add_edge('d','f',weight=1.2)
g.add_edge('f','g',weight=2.2)
g.add_edge('f','h',weight=2.2)
g.add_edge('h','i',weight=2.2)
g.add_edge('i','l',weight=1.0)
g.add_edge('l','m',weight=0.5)
g.add_edge('l','n',weight=2.2)

print g.number_of_nodes()
#print g.number_of_edges()
#print g.nodes()
#print g.edges()

# for node in g.nodes():
#     print node,g.degree(node)
print nx.shortest_path(g,'c','n')

shape = nx.read_shp(r"C:\data\tools\sparc\conflicts/GDELTSU.shp")
rete_shp = nx.DiGraph(shape)

nx.draw(shape)
#nx.draw_random(rete_shp)
#nx.draw_circular(shape)
#nx.draw_spectral(shape)
pos=nx.spring_layout(rete_shp) # positions for all nodes

#Betweenness centrality
bet_cen = nx.betweenness_centrality(rete_shp)

#Closeness centrality
clo_cen = nx.closeness_centrality(rete_shp)

#Eigenvector centrality
eig_cen = nx.eigenvector_centrality(rete_shp)

print bet_cen
print clo_cen
print eig_cen

plt.show()

