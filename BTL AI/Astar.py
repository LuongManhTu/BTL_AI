import math
import queue
from Xu_Ly_Danh_Sach_Dinh_Ke import matran_dinhke
from DS_Node import danh_sach_node


class Node:
    def __init__(self, index, g, h):
        self.index = index
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, orther):
        return self.f < orther.f


def Astar(matran_dinhke, danh_sach_node, start, goal):
    result = []
    n = len(danh_sach_node)
    b = [0.0] * 100
    distance = [[0.0] * n for _ in range(n)]

    for j in range(n):
        b[j] = math.sqrt((danh_sach_node[j].vi_tri_x - danh_sach_node[goal].vi_tri_x)
                         ** 2 + (danh_sach_node[j].vi_tri_y - danh_sach_node[goal].vi_tri_y) ** 2)

    for i in range(n):
        for j in range(n):
            distance[i][j] = 0
            if matran_dinhke[i][j] != -2:
                if(i!=0 or j !=2):
                    distance[i][j] = math.sqrt((danh_sach_node[i].vi_tri_x - danh_sach_node[j].vi_tri_x) ** 2 + (
                        danh_sach_node[i].vi_tri_y - danh_sach_node[j].vi_tri_y) ** 2)
                else:
                    distance[i][j] = math.sqrt((danh_sach_node[i].vi_tri_x - danh_sach_node[j].vi_tri_x) ** 2 + (
                        danh_sach_node[i].vi_tri_y - danh_sach_node[j].vi_tri_y) ** 2)*2+ 100

    trace = {}
    diem = [Node(i, 0, b[i]) for i in range(n)]
    Open = queue.PriorityQueue()
    Close = []
    diem[start].g = 0
    Open.put(diem[start])

    while not Open.empty():

        curnode = Open.get()
        Close.append(curnode)

        if curnode.index == goal:

            u = curnode

            while u.index != start:
                result.append(u.index)
                u = trace[u]
            result.append(u.index)
            result.reverse()
            return result

        for i in range(n):
            if distance[curnode.index][i] != 0:
                neibor = diem[i]
                if neibor not in Open.queue and neibor not in Close:
                    trace[neibor] = curnode
                    neibor.g = curnode.g + distance[curnode.index][i]
                    neibor.f = neibor.g + neibor.h
                    Open.put(neibor)
