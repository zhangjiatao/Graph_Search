#coding=utf-8
from aip import AipNlp
from py2neo import Node, Relationship, Graph
from time import time
import sys


def lexer(text):
	'''
	分词工具
	param : string
	return : list
	'''

	""" 你的 APPID AK SK """
	APP_ID = '11167723'
	API_KEY = 'gVD3AUIEGn0KXtUVUur5EQFe'
	SECRET_KEY = 'jQ3d2hnKUlWD1Br0Ns9bDOUvwTdHvxr5'

	client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

	ans = client.lexerCustom(text)['items'] #调用词法分析
	#print(ans)

	return ans

def extract(items):
	'''
	信息提取
	param : list
	return : dict
	'''
	# 问题词qword(who,how,what)，问题焦点qfocus(答案类型name, time, place)，问题主题词qtopic(命名实体)和问题中心动词qverb()
	'''
	qtype   问句类型
	  0	  默认类型：询问实体
	  1   计数
	  2   询问当前实体属性
	  3   询问当前实体(不指向某一属性)
	'''
	info = {'qword':'', 'qfocus':'', 'qtopic':'', 'qverb':'', 'qtype':0}

	for item in items:
		if item['ne'] == 'LOC':
			info['qtopic'] = item['item']

		elif item['pos'] == 'v':
			info['qverb'] = item['item']

		elif item['pos'] == 'n':
			info['qfocus'] = item['item']

		elif item['pos'] == 'r':
			info['qword'] = item['item']

	return info


def alignment(info):
	'''
	实体对齐
	param : dict
	return : dict
	'''
	qfocus_dict = {
		'国家级':'国家级', '国家':'国家级', '国':'国家级',
		'省级':'省级', '省':'省级',
		'地市级':'地市级', '市':'地市级',
		'县级':'县级', '县':'县级', '区级':'县级', '区':'县级',
		'乡级':'乡级', '乡':'乡级',
		'村级':'村', '村':'村',
		'水电站':'水电站',
		'大坝':'大坝',
		'水库':'水库'
	}

	qverb_dict = {
		'属于':'BELONGS_TO',
		'有' : 'BELONGS_TO',
	}

	qtype_dict = {
		'多少':1,
		'几个':1,
	}

	property_dict = {
		'多大':'面积', '面积':'面积',
		'级别':"行政区划级别",
		'代码':"行政区划代码", '编号':"行政区划代码",
		'全称':'行政区划全称',
		'简称':'行政区划简称',
		'行政中心':"行政驻地", '行政驻地':"行政驻地",

	}

	# 判断类型
	if info['qword'] in qtype_dict.keys():
		info['qtype'] = qtype_dict[info['qword']]

	# 目标类型对齐
	if info['qfocus'] in qfocus_dict.keys():
		info['qfocus'] = qfocus_dict[info['qfocus']]
	elif info['qfocus'] in property_dict.keys():# 如果询问类型不落在目标类型中，则为属性询问
		info['qfocus'] = property_dict[info['qfocus']]
		info['qtype'] = 2
	elif info['qfocus'] == '':
		info['qtype'] = 3

	for k, v in qverb_dict.items():
		if info['qverb'] in k:
			info['qverb'] = v

	return info



def createCypher(info, g):
	'''
	创建搜索语句
	param : dict
	return : string list
	'''
	candidate_list = []

	entity_list = [] # 搜索起点列表
	entity_list.append('match(s{行政区划简称:\'%s\'})' % info['qtopic'])
	entity_list.append('match(s{标题:\'%s\'})' % info['qtopic'])


	#获取实体节点的级别信息并进行过滤#
	entity_type = ''
	for entity_Cypher in entity_list[::-1]:
		res = g.data(entity_Cypher + " return s")

		if len(res) != 0:
			entity_type = res[0]['s']['行政区划级别']

		else:
			entity_list.remove(entity_Cypher)

	# 如果询问类型是询问当前实体类型，那么直接返回，否则进行加边操作
	if info['qtype'] == 2 or info['qtype'] == 3:

		for entity_Cypher in entity_list:
			candidate_list.append([entity_Cypher, -1])

		return entity_list, candidate_list

	# 寻找距离
	level_dict = {
		'国家级': 1,
		'省级': 2,
		'地市级': 3,
		'县级': 4,
		'乡级': 5,
		'村': 6,
		'水电站': 6,
		'大坝': 6,
		'水库':6,

	}
	dis = abs(level_dict[entity_type] - level_dict[info['qfocus']])

	for index, entity_Cypher in enumerate(entity_list):
		candidate = entity_Cypher

		# 加班产生候选搜索语句candidate
		for j in range(dis - 1):
			# candidate = candidate + '-[:%s]-()' % info['qverb']
			candidate = candidate + '-[]-()'
		#candidate = candidate + '-[:%s]-(ans:%s)' % (info['qverb'], info['qfocus'])
		candidate = candidate + '-[]-(ans:%s)' % (info['qfocus'])
		candidate_list.append([candidate, index]) # 将该候选搜索语句和其对应的搜索起点下标一起放入candidate_list
	return entity_list, candidate_list

def search(text, qtype, g):
	'''
	进行搜索
	'''
	if qtype == 0 or qtype == 1:
		res = g.data(text + ' return ans')
		return res
	# if qtype == 1:
	# 	res = g.data(text + ' return count(ans)')
	#	return res
	if qtype == 2 or qtype == 3:
		res = g.data(text + ' return s')
		return res

def packAns(entity_list, candidate_list, info, g):


	A_list = []  # 答案列表
	node_list = [] # 相关节点列表
	edges_graph = [] # 图谱边列表
	nodes_graph = [] # 图谱点列表

	for entity_s in entity_list:
		tmp = search(entity_s, 2, g)[0] #这里假设每个起始点在neo4j中只能找到一个对应的实体，实际也应该保证这样
		node_list.append(tmp['s'])

	# 搜索答案
	# candidate应该是一个list，0位表示候选问句，1位表示其对应的起始实体
	for candidate in candidate_list:
		ans = search(candidate[0], info['qtype'], g)
		ans_message = '' # 用来存储问题直接的答案

		# 对于询问起始实体经过关系查询到的类型0
		if info['qtype'] == 0:
			if len(ans) != 0:
				for tmp in ans:

					ans_message = tmp['ans']['标题']
					A_list.append(ans_message)
					node_list.append(tmp['ans'])
					edges_graph.append({'source' : candidate[1], 'target' : len(node_list) - 1})
					print ('A:',tmp['ans']['标题'])

		# 对于计数类询问，添加计数结果到A_list，node_list和edges_graph添加操作同上
		elif info['qtype'] == 1:
			if len(ans) != 0:
				# 填写A_list
				ans_message = str(len(ans)) + "个"
				A_list.append(ans_message)
				# 填充node_list 和edge_list
				for tmp in ans:
					node_list.append(tmp['ans'])
					edges_graph.append({'source' : candidate[1], 'target' : len(node_list) - 1})
					print ('A:',tmp['ans']['标题'])

		# 对于询问起始节点属性，添加计数结果到A_list，node_list和edges_graph添加操作同上
		elif info['qtype'] == 2:
			if len(ans) != 0:
				for tmp in ans:
					ans_message = tmp['s'][info['qfocus']]
					A_list.append(ans_message)
					#node_list.append(tmp['s']) #因为在2这种情况下起始点已经被加入node_list中了
					print ('A:',tmp['s'][info['qfocus']])

		elif info['qtype'] == 3:
			if len(ans) != 0:
				for tmp in ans:
					ans_message = tmp['s']['标题']
					A_list.append(ans_message)
					#node_list.append(tmp['s']) #因为在3这种情况下起始点已经被加入node_list中了
					print ('A:',tmp['s']['标题'])

	for node in node_list:
		nodes_graph.append({'name' : node['标题']})

	return A_list, node_list, edges_graph, nodes_graph

def workflow(s, visual_flag, g):

	START_TIME = time()

	print ('Q:',s)
	if(visual_flag == 1):
		print ('----------------------')

	# 进行分词
	ans = lexer(s)

	if(visual_flag == 1):
		for i in ans:
			print (i['item'], i['pos'])
		print ('----------------------')

	# 信息抽取
	info = extract(ans)

	if(visual_flag == 1):
		for k, v in info.items():
			print (k, v)
		print ('----------------------')

	# 实体对齐
	info = alignment(info)

	if(visual_flag == 1):
		for k, v in info.items():
			print (k, v)
		print ('----------------------')

	# 创建Cypher语句
	entity_list, candidate_list = createCypher(info, g)

	if(visual_flag == 1):
		for i in candidate_list:
			print (i)
		print ('----------------------')

	# 按照问句类型对答案进行整理打包
	A_list, node_list, edges_graph, nodes_graph = packAns(entity_list, candidate_list, info, g)


	time_cost = "%.3fs" % (time() - START_TIME)
	print ("本次搜索总计用时:%.3fs" % (time() - START_TIME))
	# print ('------------------ans_list------------------')
	# print (A_list)
	# print ('------------------node_list------------------')
	# print(node_list)
	# print ('------------------edges_graph------------------')
	# print(edges_graph)
	# print ('------------------nodes_graph------------------')
	# print(nodes_graph)
	# print ('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

	return time_cost, A_list, node_list, edges_graph, nodes_graph

# if __name__ == '__main__':


# 	visual_flag = 0;
# 	if(len(sys.argv) == 2):
# 		if(sys.argv[1] == 'v'):
# 			visual_flag = 1;

# 	query_list = [
# 		 # 直接对实体询问
# 		 # '南京',
# 		 # '包头',
# 		 # '江宁区的水库有多少？',
# 		 # '江宁区的大坝有哪些？',
# 		 # '江宁区的水电站有哪些？',
# 		 # # '国务院三峡工程建设委员会办公室', # 尚存问题，因为无法构造用户词典，这个名词会被拆开
# 		 # # # 询问实体属性
# 		 # '包头的面积是多少？',
# 		 # '南京的编号是多少？',
# 		 # '南京的全称是什么？',
# 		 # # 计数类型
# 		 # '南京市有多少个区？', # 计数类型
# 		 # # '江苏省有多少个村？', # 计数类型
# 		 # # 询问实体类型
# 		 # '包头有哪些区？',	# 询问实体类型(一或多)
# 		 # '包头属于哪个省?',
# 		 # '南京属于哪个省？',
# 		 # '江苏有哪些市？',
# 		 # '南京有哪些区？',
# 		 # # TODO
# 		 # '江苏省面积在50000以上的市有哪些？'

# 	]

# 	g = Graph(password = '123456')

# 	for query in query_list:
# 		time_cost, A_list, node_list, edges_graph, nodes_graph = workflow(query, visual_flag, g)