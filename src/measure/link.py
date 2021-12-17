"""
spread of excitation
"""
import numpy as np

def component_get_zxy(blobs,component):
    zxy = []
    for node in component:
        xy = blobs[node[0]][node[1]].pixels
        z = np.full((len(xy),1),node[0])
        zxy.append(np.hstack((z,xy)))
    return np.vstack(zxy).astype(int)

def unique_xy(xys):
    return set(tuple(xy) for xy in xys)
    
def component_cum_area(blobs,component):
    zxy = component_get_zxy(blobs,component)
    return len(unique_xy(zxy[:,1:]))

def cc_area(cc,blobs):#cumulative
    return np.array([component_cum_area(blobs,component) for component in cc])
    
def cc_area_newexc(cc,blobs):##sum of NEWEXC area in each component
    result = np.zeros(len(cc))
    for i,component in enumerate(cc):
        for node in component:
            b = blobs[node[0]][node[1]]
            result[i] += b.pixels_NEWEXC.sum()
    return result

def cc_sort_by_measurefunc(cc,blobs,measurefunc):
    measured = measurefunc(cc,blobs)
    sortidx = np.argsort(measured*-1)
    return cc[sortidx],measured[sortidx]

def blob_distance(b_current,b_previous):
    result = 0
    xy_current,xy_previous = b_current.pixelsp,b_previous.pixelsp
    len_current,len_previous = len(xy_current),len(xy_previous)
    overlap = len(set(xy_current)&set(xy_previous))
    overlap_frac = max(overlap/len_current,overlap/len_previous)
    if overlap>8:
        result = overlap_frac
    return result

def link(blobs,threshold_xy,threshold_z):
    import itertools
    zs = list(blobs.keys())
    dzs = 1+np.arange(threshold_z)
    edges = []
    for z_current in zs[1:]:
        for dz in dzs:
            z_previous = z_current-dz
            n_current,n_previous = len(blobs[z_current]),len(blobs[z_previous])
            if z_previous not in zs:
                continue
            if n_current==0 or n_previous==0:
                continue
            for i_current,i_previous in itertools.product(np.arange(n_current),np.arange(n_previous)):#
                n1,n2 = (z_previous,i_previous),(z_current,i_current)
                d = blob_distance(blobs[z_current][i_current],blobs[z_previous][i_previous])
                #print((n1,n2,d),end=',   ')
                if d>threshold_xy:
                    edges.append((n1,n2,d))
                    
    return blobs,edges

def connected_components(blobs,link_threshold_xy=0.1,link_threshold_frames=1,example=False):
    blobs,edges = link(blobs,link_threshold_xy,link_threshold_frames)#unit: pixels,frames(1.2s)
    import networkx as nx
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(edges)
    graph = nx.algorithms.dag.transitive_reduction(graph)
    
    cc = np.array(list(nx.connected_components(graph.to_undirected())))
    cc,area = cc_sort_by_measurefunc(cc,blobs,cc_area)
    if not example:
        return area[0]

    for label,component in enumerate(cc):
        for pz,j in component:
            blobs[pz][j].label = label
    return blobs, graph, cc, area

