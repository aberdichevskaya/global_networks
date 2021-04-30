#!/usr/bin/env python
# coding: utf-8

# In[1]:


import hashlib
import threading
import random
import math
import string
import networkx as nx
import matplotlib.pyplot as plt
import time


# In[2]:


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


# In[3]:


class node:
    def __init__(self, num):
        self.id = num
        self.routing_table = []
        self.routing_table_ids = []
        self.files = []
        
    def find_root(self, goal):
        goal = (str(goal))
        cur = (str(self.id))
        idx_goal = 0
        idx_cur = 0
        for l in self.leaves:
            if goal == l.id:
                return l
        while idx_goal < len(goal) and idx_cur < len(cur) and goal[idx_goal]==cur[idx_cur]:
            idx_goal += 1
            idx_cur += 1
        if idx_cur == len(cur) or idx_goal==len(goal):
            return self
        if self.routing_table[idx_cur][int(goal[idx_goal])] == None:
            return self
        else:
            return self.routing_table[idx_cur][int(goal[idx_goal])].find_root(goal)
        
    def find_file(self, goal, path = [], depth = 0):
        for l in self.leaves:
            if goal == l.id:
                return 1, depth
        path.append(self.id)
        goal = (str(goal))
        cur = (str(self.id))
        idx_goal = 0
        idx_cur = 0
        while idx_goal < len(goal) and idx_cur < len(cur) and goal[idx_goal]==cur[idx_cur]:
            idx_goal += 1
            idx_cur += 1
        if (idx_cur>=len(cur) or idx_goal>=len(goal) or
           self.routing_table[idx_cur][int(goal[idx_goal])] == None or goal in self.files):
            if goal in self.files:
                return 1, depth
            else:
                return 0, depth
        else:
            return self.routing_table[idx_cur][int(goal[idx_goal])].find_file(goal, path, depth+1)
        
        
    def add_edge(self, n):
        flag = False
        for level in self.routing_table:
            for l in level:
                if not l:
                    l = n
                    flag = True
                    break
            if flag:
                break
                    
                    
    def find_neighbours(self):
        self.neighbours = []
        for i in range(10):
            idx = random.randint(0, len(self.hosts)-1)
            self.neighbours.append(self.hosts[idx])
            
            
    def find_leaves(self, hosts):
        self.leaves = []
        idx = 0
        for h in hosts:
            if h == self.id:
                break
            idx +=1
        for i in range(5):
            self.leaves.append(hosts[(idx+i)%len(hosts)])
            self.leaves.append(hosts[(idx-i+len(hosts))%len(hosts)])
        
    def dfs(self, used = {}):
        used[self.id] = 1
        for level in self.routing_table:
            for to in level:
                if to and not to.id in used:
                    to.dfs(used)


# In[4]:


class net:
    def __init__(self, n):
        self.ring_size = 1000000
        self.nodes_cnt = n
        self.id_to_node = {}
        self.nodes = []
        self.build_graph()
       
    def generate_vertexes(self):
        hosts = []
        for i in range(self.nodes_cnt):
            host_id = net.get_id(net.ip_generator(), self.ring_size)
            hosts.append(host_id)
        hosts.sort()
        return hosts
        
    def find_links(self, host):
        host = str(host) 
        prefix = ""
        links = []
        for i in range(len(host)):
            links_on_level = []
            for k in range(8):
                curr = prefix+str(k)
                if host.startswith(curr):
                    links_on_level.append(None)
                    continue
                suitable_nodes = []
                for neighbour in self.hosts:
                    st = str(neighbour)
                    if st.startswith(curr):
                        suitable_nodes.append(neighbour)
                if len(suitable_nodes)==0:
                    links_on_level.append(None)
                    continue
                idx = random.randint(0, len(suitable_nodes)-1)
                links_on_level.append(suitable_nodes[idx])
            links.append(links_on_level)
            prefix += host[i]
        return links
        
    
        
    def build_graph(self):
        self.hosts = self.generate_vertexes()
        for host in self.hosts:
            new_node = node(host)
            self.id_to_node[host] = new_node
            self.nodes.append(new_node)
            idx = len(self.nodes)-1
            self.nodes[idx].routing_table_ids = self.find_links(host)
            self.nodes[idx].files = net.files_generator(self.ring_size)
            self.nodes[idx].find_neighbours()
            self.nodes[idx].find_leaves(self.hosts)
        self.fix_links()
        
        self.fix_connection()
                
    def fix_links(self):
        for n in self.nodes:
            #print(n.routing_table_ids)
            links = []
            for level in n.routing_table_ids:
                links_on_level = []
                for link in level:
                    if(link):
                        links_on_level.append(self.id_to_node[link])
                links.append(links_on_level)
            n.routing_table = links
      
    def move_files(self):
        for n in self.nodes:
            res = []
            for file in n.files:
                root = n.find_root(file)
                res.append(file)
            if(root):
                root.files += res
    
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
            file = net.get_id(file_name, mod)
            files.append(net.get_id(file, mod))
        return files
    
  
    
    def fix_connection(self):
        used = {}
        last = None
        for n in self.nodes:
            #print(n.id)
            #print(used)
            if not n.id in used:
                if last:
                    last.add_edge(n)
                last = n
                n.dfs(used)
                
    


# In[ ]:


G = net(100)


# In[ ]:


def send_queries(G, queries_cnt):
    min_depth = 1000000000
    max_depth = 0
    average_depth = 0
    were_found = 0
    for vertex in G.nodes:
        #print("мы находимся в компьютере ", vertex.id)
        for query in range(queries_cnt):
            #print("ищем в сети рандомный файл")
            length = random.randint(0, 30) 
            file_to_find = generate_random_string(length)
            was_found, depth = vertex.find_file(net.get_id(file_to_find, 2**(G.ring_size)))
            min_depth = min(min_depth, depth)
            max_depth = max(max_depth, depth)
            average_depth += depth
            were_found += was_found
            #print(depth)
        average_depth /= queries_cnt
    return min_depth, max_depth, average_depth, were_found


# In[ ]:


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
        
    node_colors = ['pink']*(len(gr.nodes))
    nx.draw_circular(gr, with_labels = True, node_color=node_colors)
    img_name = "Graph" + "_before" + ".png"
    plt.savefig(img_name, format="PNG")
    
    if len(path) == 0:
        return 

    for i in range(len(path) - 1):
        node_colors[nodes[path[i]]] = 'red'
        nx.draw_circular(gr, with_labels = True, node_color=node_colors)
        img_name = "Graph" + str(i) + ".png"
        plt.savefig(img_name, format="PNG")
    node_colors[nodes[path[len(path)-1]]] = 'red'
    nx.draw_circular(gr, with_labels = True, node_color=node_colors)
    
    img_name = "Graph" + "done" + ".png"
    plt.savefig(img_name, format="PNG")


# In[ ]:


queries_cnt = 10

print("начинаем тестировать")
min_depth, max_depth, average_depth, were_found = send_queries(G, queries_cnt)
print()

print("минимальная длина пути ", min_depth)
print("максимальная длина пути ", max_depth)
print("средняя длина пути ", average_depth)


# In[ ]:


little_net = net(20)
vertex = little_net.nodes[0]
file_to_find = generate_random_string(3)
path = []
was_found, depth = vertex.find_file(141, path)
graph_visualization(little_net, path)

