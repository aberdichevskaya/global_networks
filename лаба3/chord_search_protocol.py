#!/usr/bin/env python
# coding: utf-8

# In[159]:


import hashlib
import threading
import random
import math
import string
import networkx as nx
import matplotlib.pyplot as plt
import time


# In[ ]:





# In[ ]:





# In[160]:


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


# In[208]:


class vertex:
    def __init__(self, size, num):
        self.ring_size = size
        self.id = num
        self.fingers_ids = []
        self.fingers = []
        self.files = []
        self.successor = self
        
    def find_successor(self, goal):
        #print("ищём id", goal, "из вершины ", self.id)
        #print("наш потомок - ", self.successor.id)
        if (self.id < goal) + (goal <= self.successor.id) + (self.successor.id < self.id) >= 2:
            #print("нашли вершину! это ", self.successor.id)
            return self.successor
        else:
            node = self.closest_preceding_node(goal)
            return node.find_successor(goal)
        
    def find_file(self, goal, path = [], depth=0):
        path.append(self.id)
        if goal in self.files:
            return 1, depth
        if ((self.id < goal) + (goal <= self.successor.id) + (self.successor.id < self.id) >= 2 or goal in self.successor.files):
            if goal in self.successor.files:
                return 1, depth+1
            else:
                return 0, depth+1
            return self.successor
        else:
            node = self.closest_preceding_node(goal)
            return node.find_file(goal, path, depth+1)
        

    def closest_preceding_node(self, goal):
        #print("ищём, куда нам дальше идти")
        for i in range(self.ring_size-1, -1, -1):
            #print("проверяем палец ", self.fingers[i].id)
            if (self.id < self.fingers[i].id) + (self.fingers[i].id < goal) + (goal < self.id) >= 2:
                #print("нашли палец")
                return self.fingers[i]
        #print("не нашли, идём в в своего потомка")
        return self.successor


# In[211]:


class graph:
    def __init__(self, n):
        self.ring_size = 2* int(math.log(n, 2))
        self.vertexes_cnt = n
        self.id_to_node = {}
        self.files_cnt = []
        print('создали поля')
        self.build_graph()
        print('построили граф')
        self.fix_fingers()
        print('положили в пальцы указатели на вершины')
        self.move_files()
        print('передвинули файлы туда, где им положено лежать')
        
    
    def generate_vertexes(self):
        ring = [0]*(2**self.ring_size)
        for i in range(self.vertexes_cnt):
            host = graph.ip_generator()
            ring[graph.get_id(host, int(2**self.ring_size))] = 1
        return ring
        
    def build_graph(self):
        #print('начали строить граф')
        vertexes_place = self.generate_vertexes()
        #print('вершины тут: ', vertexes_place)
        #print('id вершин сгенерированы')
        self.vertexes = []
        for i in range(int(2**self.ring_size)):
            if vertexes_place[i] == 1:
                #print('добавляем вершину с id ', i)
                new_node = vertex(self.ring_size, i)
                #print('создали новый узел сети с id ', i)
                self.vertexes.append(new_node)
                self.id_to_node[i] = new_node
                #print('сохранили вершину и её id')
                idx = len(self.vertexes)-1
                for num in range(self.ring_size):
                    #print('ищём палец номер ', num+1, ' вершины номер ', idx, ', id = ', i)
                    j = (i + int(2**num))% int(2**self.ring_size)
                    while vertexes_place[j] != 1:
                        j = (j + 1) % int(2**self.ring_size)
                    self.vertexes[idx].fingers_ids.append(j) 
                    #print('найденный палец имеет id ', j)
                #print('нашли все пальцы для вершины номер ', idx)
                #print('генерим файлы для вершины номер ', idx)
                self.vertexes[idx].files = graph.files_generator(int(2**self.ring_size))
                self.files_cnt += self.vertexes[idx].files
                #print('файлы сгенерированы')
        
    def fix_fingers(self):
        for v in self.vertexes:
            #print(v.fingers_ids)
            for finger in v.fingers_ids:
                v.fingers.append(self.id_to_node[finger])
            v.successor = v.fingers[0]
    
    def move_files(self):
        for v in self.vertexes:
            res = []
            for file in v.files:
                node = v.find_successor(file)
                res.append(file)
            if(node):
                node.files += res
    
    
    def get_id(st, mod):
        string = str(st)
        return int(hashlib.sha1(string.encode()).hexdigest(), 16) % mod
        
    def ip_generator():
        a = random.randint(0,255)
        b = random.randint(0,255)
        c = random.randint(0,255)
        d = random.randint(0,255)
        return str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)
        
    def files_generator(mod):
        files = []
        cnt = random.randint(0, 30)
        for i in range(cnt):
            length = random.randint(0, 30)
            file_name = generate_random_string(length)
            file = graph.get_id(file_name, mod)
            files.append(graph.get_id(file, mod))
        return files


# In[198]:


def send_queries(graphs_cnt, queries_cnt):
    min_depth = 1000000000
    max_depth = 0
    average_depth = 0
    were_found = 0
    for g in range(graphs_cnt):
        G = graph(1000)
        for vertex in G.vertexes:
            #print("мы находимся в компьютере ", vertex.id)
            for query in range(queries_cnt):
                #print("ищем в сети рандомный файл")
                length = random.randint(0, 30) 
                file_to_find = generate_random_string(length)
                was_found, depth = vertex.find_file(graph.get_id(file_to_find, 2**(vertex.ring_size)))
                min_depth = min(min_depth, depth)
                max_depth = max(max_depth, depth)
                average_depth += depth
                were_found += was_found
                #print(depth)
            average_depth /= queries_cnt
    return min_depth, max_depth, average_depth, were_found


# In[206]:


def check_amount_information(G):
    min_amount_files = 1000000000
    max_amount_files = 0
    average_amount_files = 0
    
    min_amount_fingers = 1000000000
    max_amount_fingers = 0
    average_amount_fingers = 0
    
    
    for vertex in G.vertexes:
        files_cnt = len(vertex.files)
        min_amount_files = min(min_amount_files, files_cnt)
        max_amount_files = max(max_amount_files, files_cnt)
        average_amount_files += files_cnt
    
        fingers_cnt = len(vertex.fingers)
        min_amount_fingers = min(min_amount_fingers, fingers_cnt)
        max_amount_fingers = max(max_amount_fingers, fingers_cnt)
        average_amount_fingers += fingers_cnt
        
    files_info = [min_amount_files, max_amount_files, average_amount_files/len(G.vertexes)]
    fingers_info = [min_amount_fingers, max_amount_fingers, average_amount_fingers/len(G.vertexes)]
        
    return files_info, fingers_info 


# In[177]:


def graph_visualization(G, path = []):
    gr = nx.DiGraph()
    sorted(G.vertexes, key=lambda n: n.id)
    edges = {}
    for vertex in G.vertexes:
        gr.add_edge(vertex.id, vertex.successor.id)
        for finger in vertex.fingers:
            gr.add_edge(vertex.id, finger.id)
    nodes = {}
    idx = 0
    for node in gr.nodes:
        nodes[node] = idx
        idx += 1
    node_colors = ['orange']*(len(gr.nodes))
    nx.draw_circular(gr, with_labels = True, node_color=node_colors)
    img_name = "Graph" + "_before" + ".png"
    plt.savefig(img_name, format="PNG")
    print("начинаем идти")
    
    if len(path) == 0:
        return 
    
    for i in range(len(path) - 1):
        #time.sleep(5)
        node_colors[nodes[path[i]]] = 'red'
        nx.draw_circular(gr, with_labels = True, node_color=node_colors)
        img_name = "Graph" + str(i) + ".png"
        plt.savefig(img_name, format="PNG")
    node_colors[nodes[path[len(path)-1]]] = 'red'
    nx.draw_circular(gr, with_labels = True, node_color=node_colors)
    
    img_name = "Graph" + "_last" + ".png"
    plt.savefig(img_name, format="PNG")


# In[212]:


G = graph(1000)


# In[213]:


print("проверка количества хранимой в узлах информации")
files_info, fingers_info  = check_amount_information(G)

print("минимально в одной вершине хранится ", files_info[0], "файлов и ", fingers_info[0], "указателей на другие вершины")
print("максималь в одной вершине хранится ", files_info[1], "файлов и ", fingers_info[1], "указателей на другие вершины")
print("в среднем в одной вершине хранится ", files_info[2], "файлов и ", fingers_info[2], "указателей на другие вершины")


# In[214]:


print(len(G.files_cnt))


# In[174]:


queries_cnt = 1000
graphs_cnt = 10

print("начинаем тестировать")
min_depth, max_depth, average_depth, were_found = send_queries(graphs_cnt, queries_cnt)
print()

print("минимальная длина пути ", min_depth)
print("максимальная длина пути ", max_depth)
print("средняя длина пути ", average_depth)


# In[199]:


little_graph = graph(15)


# In[200]:


vertex = little_graph.vertexes[0]
file_to_find = generate_random_string(length)
path = []
print(vertex.id)


# In[201]:


was_found, depth = vertex.find_file(2, path)


# In[202]:


print(path)
print(graph.get_id(file_to_find, 2**(vertex.ring_size)))


# In[203]:


graph_visualization(little_graph, path)


# In[180]:


G = graph(30)
graph_visualization(G)


# In[ ]:




