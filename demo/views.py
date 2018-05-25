from django.shortcuts import render

# Create your views here.


from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_protect
from py2neo import Node, Relationship, Graph
import json
import re
import time
from django.db.models import Q
from demo.search_demo import workflow



# 获取工作经验要求分布情况
def getSearch_result(request):
    if request.method == 'GET':
        try:
            s = request.GET.get('text')
            #s = '包头属于哪个省？'
            print (s)
            visual_flag = 0
            g = Graph(password='123456')
            time_cost, A_list, node_list, edges_graph, nodes_graph = workflow(s, visual_flag, g)

        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({'msg': '1'}), content_type="application/json;charset=utf-8")
        return HttpResponse(json.dumps({'time':time_cost,'msg': '0', 'anslist': A_list, 'nodeList': node_list, 'edgesGraph' : edges_graph,'nodesGraph': nodes_graph}), content_type="application/json;charset=utf-8")
    else:
        return Http404