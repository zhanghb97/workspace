# -*- coding: UTF-8 -*-

class Vertex(object):
    # 顶点类，包含本身key信息，和邻接的边list
    def __init__(self, key):
        self.key = key
        self.next = []

class Edge(object):
    # 边类，包含起始节点、终止节点、权重，三个成员变量
    def __init__(self, fromNode, toNode, weight):
        self.fromNode = fromNode
        self.toNode = toNode
        self.weight = weight

class Graph(object):
    # 图类，包含顶点的集合、顶点数量，两个成员变量
    def __init__(self):
        self.vertList = [] 
        self.numVertices = 0

    # 添加节点，像图类的顶点list中添加节点
    def addVertex(self, key):
        newVertex = Vertex(key)
        self.vertList.append(newVertex)
        self.numVertices = self.numVertices + 1

    # 添加边，将指定的两个顶点生成一个边对象，并存入节点数组中
    def addEdge(self, fromNode, toNode, weight):
        newEdge = Edge(fromNode, toNode, weight)
        # TODO: 此处应判断如果节点未在图中，如何处理
        self.vertList[fromNode].next.append(newEdge)
        self.vertList[toNode].next.append(newEdge)

if __name__ == '__main__':
    # 实例化图类
    g = Graph()

    # 给邻接表添加节点
    for i in range(6):
        g.addVertex(i)
    
    # 给邻接表添加边信息
    g.addEdge(0, 5, 2) 
    g.addEdge(1, 2, 4) 
    g.addEdge(2, 3, 9) 
    g.addEdge(3, 4, 7) 
    g.addEdge(3, 5, 3) 
    g.addEdge(4, 0, 1) 
    g.addEdge(5, 4, 8) 
    g.addEdge(5, 2, 1) 

    # 输出邻接表信息
    for v in g.vertList:                                      
        print("Vertex: " + str(v.key) + "\nEdge:")
        for e in v.next:
            print("(" + str(e.fromNode) + "," + str(e.toNode) + ")")