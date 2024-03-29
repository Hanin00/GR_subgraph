from utils import utils, subgraph
from cbir_subsg import models
# from cbir_subsg.conf_all import parse_encoder
from cbir_subsg.conf import parse_encoder

import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import Counter

import os, sys
import torch
import argparse
import pickle
import time
import tqdm

import numpy as np

import networkx as nx
import matplotlib.pyplot as plt



'''
    1103
    0에 가까울 수록 비슷한 것


    0731 - 기존과 달라진 점
    1. 서브그래프를 사용하지 않음
    2. 그래프 형식이 다름 - edge feature 있음;

    db_idx.extend([i]*len(datas))# 기존에는 그래프의 id를 subgraph 개수만큼 생성
    하지만, 지금은 비디오 내 프레임별로 scenegraph 를 생성하므로 파일명과 몇 번째 그래프인지를 표현해주면 됨
    
    
    1117
    
    query Graph 출처 비디오
    ['4239231056', '7645715544']

'''

#retrieval_subgraph에서 
def load_dataset_temp(args,F0Dict):
    # with open("data/scenegraph_1/0_6096540713_6096540713.pkl", "rb") as fr:
    #     datas = pickle.load(fr)
    db = []
    db_idx = []
    
    seeds = 4
    
    max_node = 3
    R_BFS = True
    # 2430799380 빼고 해보기..?
    # filenames = ['4239231056.json.pkl', '7645715544.json.pkl','2406271188.json.pkl']
    
    # filenames = ['4239231056.json.pkl', '7645715544.json.pkl'] #2
    
    filenames = ['4239231056.json.pkl', '7645715544.json.pkl', '2406271188.json.pkl', '2430799380.json.pkl', 
    #  ] # 4
                 '3828379201.json.pkl', '4148862873.json.pkl', '5454696393.json.pkl', '5759653927.json.pkl'] #1215
    
    cnt_video = 0
    for filename in filenames:
        vId = filename.split('.')[0]
        
        with open("data/scenegraph/"+ filename, "rb") as fr:
            tmp = pickle.load(fr)            
            length = len(tmp[0]) 
            print("length : ",length)
        
            cnt_video += length
            # length = 2            
            if length != 0:
                cnt = 0
                # 'rpe' 가 없던 scenegraph에 계산해서 rpe 값 node에 넣어주는 부분
                for i in range(length):   
                    # tmp[0][i].graph['gid'] = i
                    # 서브 그래프를 만든 후에 rpe를 계산? rpe를 계산한 다음에 서브그래프를 만들어야 해당 이미지에서 해당 노드를 더 잘표현하는 것 아닌가?
                    origin_g, origin_enc_agg = utils.mkNG2Subs(tmp[0][i], args,F0Dict)  # Gs에 Feature 붙임
                    # print(origin_g.nodes(data="rpe"))
                    subs = subgraph.make_subgraph(origin_g, max_node, False, R_BFS) # subgraph 로 나눔
                    db.extend(subs)    
                    db_idx.extend([str(vId)+ '_' + str(tmp[2][i])+'_'+str(subIdx) for subIdx in range(len(subs))])                
                db_reIdx = [i for i in range(len(db))]
        # print("len(db): ", len(db)) 
        # print("len(db): ", len(db_idx)) 
    print("cnt_video: ", cnt_video)
    print("total len(db): ", len(db))
    
   
    
    # query = []
    # # user-defined query images
    # with open("data/seq_g3_4239231056_7645715544.pkl", "rb") as q:
    #     queryDataset = pickle.load(q)
    #     #todo - 여기서 RPE 계산해야함        
        
    #     length = len(queryDataset[0])
    #     if length != 0:
    #         cnt = 0
    #         query_number = [idx for idx in queryDataset[2]]
    #         for i in range(length):   
    #             # queryDataset[i].graph['gid'] = i
    #             origin_g, origin_enc_agg = utils.mkNG2Subs(queryDataset[0][i], args, F0Dict)  # Gs에 Feature 붙임
    #             query.append(origin_g)
    
    query = []
    queryDataset = [[],[],[]]
    for i in range(0, len(db_reIdx), 40):
        queryDataset[0].append(db[i])
        queryDataset[1].append(db_idx[i].split('_')[0])
        queryDataset[2].append(db_idx[i].split('_')[1])
    print(queryDataset)  
       

    length = len(queryDataset[0])
    if length != 0:
        cnt = 0
        query_number = [idx for idx in queryDataset[2]]
        for i in range(length):   
            # queryDataset[i].graph['gid'] = i
            origin_g, origin_enc_agg = utils.mkNG2Subs(queryDataset[0][i], args, F0Dict)  # Gs에 Feature 붙임

            query.append(origin_g)
    
    
    # with open("result/dataset_retrieval_target.pkl", "wb") as fw:
    with open("result/overlapped.pkl", "wb") as fw:
    # with open("result/vid08_1217_from_db.pkl", "wb") as fw:
        pickle.dump([db, db_idx, db_reIdx, query, query_number], fw)
            
                    
    return db, db_idx, db_reIdx, query, query_number


def load_dataset_query(args,F0Dict):
    # with open("data/scenegraph_1/0_6096540713_6096540713.pkl", "rb") as fr:
    #     datas = pickle.load(fr)
    db = []
    db_idx = []
    
    seeds = 4
    
    max_node = 3
    R_BFS = True
    # 2430799380 빼고 해보기..?
    # filenames = ['4239231056.json.pkl', '7645715544.json.pkl','2406271188.json.pkl']
    
    # filenames = ['4239231056.json.pkl', '7645715544.json.pkl'] #2
    
    filenames = ['4239231056.json.pkl', '7645715544.json.pkl', '2406271188.json.pkl', '2430799380.json.pkl', 
    #  ] # 4
                 '3828379201.json.pkl', '4148862873.json.pkl', '5454696393.json.pkl', '5759653927.json.pkl'] #1215
    
    cnt_video = 0
    for filename in filenames:
        vId = filename.split('.')[0]
        
        with open("data/scenegraph/"+ filename, "rb") as fr:
            tmp = pickle.load(fr)            
            length = len(tmp[0]) 
            print("length : ",length)
        
            cnt_video += length
            # length = 2            
            if length != 0:
                cnt = 0
                # 'rpe' 가 없던 scenegraph에 계산해서 rpe 값 node에 넣어주는 부분
                for i in range(length):   
                    # tmp[0][i].graph['gid'] = i
                    # 서브 그래프를 만든 후에 rpe를 계산? rpe를 계산한 다음에 서브그래프를 만들어야 해당 이미지에서 해당 노드를 더 잘표현하는 것 아닌가?
                    origin_g, origin_enc_agg = utils.mkNG2Subs(tmp[0][i], args,F0Dict)  # Gs에 Feature 붙임
                    # print(origin_g.nodes(data="rpe"))
                    subs = subgraph.make_subgraph(origin_g, max_node, False, R_BFS) # subgraph 로 나눔
                    db.extend(subs)    
                    db_idx.extend([str(vId)+ '_' + str(tmp[2][i])+'_'+str(subIdx) for subIdx in range(len(subs))])                
                db_reIdx = [i for i in range(len(db))]
        # print("len(db): ", len(db)) 
        # print("len(db): ", len(db_idx)) 
    print("cnt_video: ", cnt_video)
    print("total len(db): ", len(db))
    
    # query = []
    # # user-defined query images
    # with open("data/seq_g3_4239231056_7645715544.pkl", "rb") as q:
    #     queryDataset = pickle.load(q)
    #     #todo - 여기서 RPE 계산해야함        
        
    #     length = len(queryDataset[0])
    #     if length != 0:
    #         cnt = 0
    #         query_number = [idx for idx in queryDataset[2]]
    #         for i in range(length):   
    #             # queryDataset[i].graph['gid'] = i
    #             origin_g, origin_enc_agg = utils.mkNG2Subs(queryDataset[0][i], args, F0Dict)  # Gs에 Feature 붙임
    #             query.append(origin_g)
    
    # 짝수: 그래프 / 홀수: meta
    #[비디오-0:그래프, 1:meta][프레임][서브그래프]
    #동일 비디오, , 다른 서브그래프?
    # print(len(tmp[0])-2)
    db_idx_pair = []
    queryGList = []
    
    
    for i in range(0, len(db)-45, 40):
        # g1 = tmp[i][i].copy()
        # g2 = tmp[0][i+1].copy()
        
        g1 = db[i].copy()
        g2 = db[40+i].copy()
        
        vid_frame_info = (db_idx[i]+" + "+db_idx[40+i])
        queryG = g1.copy()
        queryG.remove_node(list(queryG.nodes())[0])
        

        if len(g2.nodes()) > 2:
            g2.remove_node(list(g2.nodes())[0])
            g2.remove_node(list(g2.nodes())[1])
            
            print(queryG.nodes(data="name"))
            print(g2.nodes(data="name"))
                        
            queryG.add_nodes_from(g2.nodes(data=True))
            queryG.add_edges_from(g2.edges())
            
            #위 방법으로 생성 시 두 그래프 간 edge 로 연결되지 않음. edge의 경우 임의로 추가해줘야함 안할래~
            print("g1: ",g1)
            print(queryG.nodes(data="name"))
            print(g1.nodes(data="name"))
            print(g2.nodes(data="name"))
            print(vid_frame_info)
            queryGList.append(queryG)
            db_idx_pair.append(vid_frame_info)
            
        else:
            print("작아")
        #continue

        # 처음 노드의 경우 겹치는 게 많음
        # g1의 경우 0번 삭제
        # g2의 경우 0번, 2번 삭제하면 여러 개 대량생산생산

    # print(len(queryGList))
    # print((queryGList))
    print("쿼리 그래프 정보")
    print(queryGList)
  
    # query = []
    # queryDataset = [[],[],[]]
    # for i in range(0, len(db_reIdx), 40):
    #     queryDataset[0].append(db[i])
    #     queryDataset[1].append(db_idx[i].split('_')[0])
    #     queryDataset[2].append(db_idx[i].split('_')[1])
    # print(queryDataset)  


    query = []
    query_number = db_idx_pair
    length = len(queryGList)
    if length != 0:
        cnt = 0
        # query_number = [idx for idx in queryDataset[2]]
        
        for i in range(length):   
            # queryDataset[i].graph['gid'] = i
            origin_g, origin_enc_agg = utils.mkNG2Subs(queryGList[i], args, F0Dict)  # Gs에 Feature 붙임
            query.append(origin_g)
            
    print("!!!!!!!!!!!!!")
    print(query)
    # with open("result/dataset_retrieval_target.pkl", "wb") as fw:
    with open("result/overlapped.pkl", "wb") as fw:
    # with open("result/vid08_1217_from_db.pkl", "wb") as fw:
        # pickle.dump([db, db_idx, db_reIdx, query, query_number], fw)
        pickle.dump([db, db_idx, db_reIdx, query, db_idx_pair], fw)
    
                    
    return db, db_idx, db_reIdx, query, query_number


def load_dataset(): #동일 조건 하에서
    # with open("result/dataset_retrieval_target.pkl", "rb") as fr:
    # with open("result/vid02_1215_sceneg_198_subg_615.pkl", "rb") as fr:
    # with open("result/vid04_1215_sceneg_935_subg_2145.pkl", "rb") as fr:
    # with open("result/vid08_1217_from_db.pkl", "rb") as fr:
    
    with open("result/overlapped.pkl", "rb") as fr:
        datas = pickle.load(fr)
        
    db, db_idx, db_reIdx, query, query_number = datas
        
    # print("query_number[-4]")        
    # print(query_number[-4])        

    # print(query[-4].nodes(data='name'))
    # print(query[-4].edges(data='predicate'))
    
    # print(query[-3].nodes(data='name'))
    # print(query[-3].edges(data='predicate'))
    
    # print(query[-2].nodes(data='name'))
    # print(query[-2].edges(data='predicate'))
    
    # print(query[-1].nodes(data='name'))
    # print(query[-1].edges(data='predicate'))
    # print(query_number[-1])
    
    print("쿼리 그래프 개수: ",len(query))
    
    
    # sys.exit()
    
                    
    return db, db_idx, db_reIdx, query, query_number





def find_duplicate_nodes_and_edges(graph1, graph2):
    common_nodes = set()
    
    # graph1에서 노드 번호와 이름 간의 대응 관계 딕셔너리 생성
    node_number_to_name_graph1 = {node_number: data.get('name') for node_number, data in graph1.nodes(data=True)}
    
    # graph2에서 노드 번호와 이름 간의 대응 관계 딕셔너리 생성
    node_number_to_name_graph2 = {node_number: data.get('name') for node_number, data in graph2.nodes(data=True)}
    
    # 공통 노드 찾기
    for node_number1, data1 in graph1.nodes(data=True):
        for node_number2, data2 in graph2.nodes(data=True):
            if data1.get('name') == data2.get('name'):
                common_nodes.add(data1.get('name'))  # 공통 노드 이름 추가
    
    common_edges = set()
    result = []
    
    for edge1, edge2, data1 in graph1.edges(data=True):
        for edge3, edge4, data2 in graph2.edges(data=True):
            # 엣지의 노드 번호를 노드 이름으로 교체
            node1_name_graph1 = node_number_to_name_graph1.get(edge1)
            node2_name_graph1 = node_number_to_name_graph1.get(edge2)
            node3_name_graph2 = node_number_to_name_graph2.get(edge3)
            node4_name_graph2 = node_number_to_name_graph2.get(edge4)

            if (node1_name_graph1 in common_nodes and node2_name_graph1 in common_nodes) and \
               (node3_name_graph2 in common_nodes and node4_name_graph2 in common_nodes):
            #    print("node 가 동일함")
            
               if data1['predicate'] == data2['predicate']:
                    # print("predicate도 동일함")
                
                #    data1.get('predicate') == data2.get('predicate'):
                    # 엣지의 'distance' 및 'angleAB' 속성 비교
                    # 
                    if 'distance' in data1 and 'distance' in data2 and \
                    'angle_AB' in data1 and 'angle_AB' in data2:
                        distance_diff = abs(data1['distance'] - data2['distance'])
                        angleAB_diff = abs(data1['angle_AB'] - data2['angle_AB'])
                    else:
                        distance_diff = None
                        angleAB_diff = None
                    
                    if data1['predicate'] == data2['predicate']:
                        predicate = data1['predicate']
                    else:
                        predicate = (data1['predicate'], data2['predicate'])
                    
                    # result.append((predicate, distance_diff, angleAB_diff, (node1_name_graph1, node2_name_graph1, data1), (node3_name_graph2, node4_name_graph2, data2)))
                    result.append((predicate, distance_diff, angleAB_diff, (node1_name_graph1, node2_name_graph1, ), (node3_name_graph2, node4_name_graph2,)))
    return result

def showGraph(graph, type, title):
    #query graph 시각화, 저장
    plt.figure(figsize = (8, 8))
    pos = nx.spring_layout(graph, k = 0.8)
    node_labels = nx.get_node_attributes(graph, 'name')    
    edge_labels = nx.get_edge_attributes(graph, 'predicate')
    # print("edge_labels: ", edge_labels)
    nx.draw_networkx_labels(graph, pos, labels=node_labels)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels = edge_labels)
    nx.draw(graph, pos, node_size = 400, node_color = 'blue',)
    plt.show()
    plt.title(type+'-'+title)
    plt.savefig('result/'+type+'/'+title+'.png',
    facecolor='#eeeeee',
    edgecolor='black',
    format='png', dpi=200)

def feature_extract(args):
    ''' Extract feature from subgraphs
    It extracts all subgraphs feature using a trained model.
    and then, it compares DB subgraphs and query subgraphs and finds0
    5 candidate DB subgraphs with similar query subgraphs.
    Finally, it counts all candidate DB subgraphs and finds The highest counted image.
    '''
    # max_node = 3
    # R_BFS = True
    # ver = 2
    
    
    with open('data/class_unique_textemb.pickle', 'rb') as f:  
        data  = pickle.load(f)
        F0Dict = data
    
    # db, db_idx, db_reIdx, query, query_number\
    # dataset, db_idx, db_reIdx, querys, query_number = load_dataset_temp(args, F0Dict)
    # sys.exit()
    
    # # 랜덤이라서 노드 개수가 3개 이상이었다 아니었다가 해서 된 걸로 사용..
    # dataset, db_idx, db_reIdx, querys, query_number = load_dataset_query(args, F0Dict)
    # sys.exit()
    
    dataset, db_idx, db_reIdx, querys, query_number  = load_dataset()   
    

    db_data = utils.batch_nx_graphs_rpe(dataset, None)
     
    # print(db_data.G[0])
    # print(db_data.G[0].nodes(data=True))
    # sys.exit()
    # print("db_data: ", len(db_data))
     
     
    # model load
    if not os.path.exists(os.path.dirname(args.model_path)):
        os.makedirs(os.path.dirname(args.model_path))
         
    model = models.GnnEmbedder(args.feature_dim, args.hidden_dim, args)  
    model.to(utils.get_device())
    if args.model_path:
        model.load_state_dict(torch.load(args.model_path, map_location=utils.get_device()))  
    else:
        return print("model does not exist")

    print("here - feature_extract")
    db_check = [{i[1] for i in d.nodes(data="name")} for d in dataset]
    temp = []


    result_graph = []
    
    # candidate_imgs = []
    # candidate_imgs_idx = []
    model.eval()
    torch.set_printoptions(precision=15)
    with torch.no_grad():
        print("len(db_data): ", len(db_data))
        print("len(db_data)[0]: ", len(db_data.G)) #12900 - 1.20601296
        extractTimeStart = time.time()  # subgraph 하나에 대한 추출 시간 - 0.001465320587
        emb_db_data = model.emb_model(db_data) # [1327,32]
        extractTimeEnd = time.time()
        print("subgraph 로 만든 db에 대한 특징 추출 시간 -+ : ", extractTimeEnd - extractTimeStart)
        print(len(querys))
        
        for idx, queryG  in enumerate(querys): #i = 쿼리 그래프의 서브 그래프 하나.
            
            if len(queryG.edges()) != 0:
                # 쿼리 그래프마다 비슷한 비디오를 검색 -> 
                candidate_imgs = []
                candidate_imgs_idx = []
                
                extractTimeStart = time.time()
                query = temp.copy()
                query.append(queryG)
                query = utils.batch_nx_graphs_rpe(query, None)
                query = query.to(utils.get_device())                  
                
                extractTimeEnd = time.time()
                
                emb_query_data = model.emb_model(query) # 서브그래프 하나에 대한 특징 추출      
                print("subGraph 하나에 대한 특징 추출 시간 -+ : ", extractTimeEnd - extractTimeStart)
                retreival_start_time = time.time()  # subgraph 하나에 대한 추출 시간
                
                sys.exit()
                
                #similarity
                # sim = torch.tensor([torch.sum(emb_query_data * emb_db_data[idx], dim=1).to(utils.get_device()) for idx in range(len(emb_db_data))] ).to(utils.get_device())
                
                sim = F.cosine_similarity(emb_query_data, emb_db_data) #1에 가까울 수록 유사한 것
                result_dict = dict(zip(db_idx, sim.cpu().numpy()))  # 토치 텐서를 넘파이 배열로 변환
                sorted_items = sorted(result_dict.items(), key=lambda item: item[1], reverse=True)  # 값을 기준으로 오름차순 정렬

                q_check = {n[1] for n in queryG.nodes(data="name")} #query graph의 name

                rIdx = 0            
                result = []
                for n, d in sorted_items[:10]:
                    # print("N: ", n)
                    # print("D: ", d)
                    # n 이 어떤 그래프이고, 해당 그래프 node에 bbox를 칠 수 있으면 더 시각화가 잘 될 것 같음                
                    result.append((n, dataset[db_idx.index(n)], db_reIdx[db_idx.index(n)]))

                    # candidate_imgs.append(n) #하나의 동영상에서 검색 시
                    candidate_imgs.append(n.split('_')[1]) #하나의 동영상에서 검색 시 + 프레임 번호까지만(동일 프레임인 경우, 묶으려고)
                    candidate_imgs_idx.append(db_reIdx[db_idx.index(n)])

                retreival_time = time.time() - retreival_start_time
                            
                # Check similar/same class count with subgraph in DB
                checking_in_db = [len(q_check) - len(q_check - i)
                                for i in db_check]
                checking_result = Counter(checking_in_db)
                # print("checking_result: ", checking_result)

                # Check similar/same class with subgraph in DB
                value_checking_in_db = [
                    str(q_check - (q_check - i))  for i in db_check]
                value_checking_result = Counter(value_checking_in_db)
                
                print(value_checking_result)
                print("==="*20)
                print("쿼리 번호: ",idx)
                print("쿼리 info: ",query_number[idx])
                print("쿼리 그래프 node: ", queryG.nodes(data="name"))
                print("쿼리 그래프 edge: ", queryG.edges(data="predicate"))
                
                
                # print(candidate_imgs) #  image frame
                # print(candidate_imgs_idx) # db 내 idx
                
                # print("@@@")
                # print(sorted_items[:10])  #이미지 영상_프레임_서브그래프 번호 정보     
                # print(dataset[candidate_imgs_idx[-1]]) #db내 해당 그래프 객체
                
                
                rank_list = [dataset[candidate_imgs_idx[cidx]] for cidx in range(len(candidate_imgs_idx))]
                result_graph.extend((rank_list, sorted_items[:20]))
            else:
                continue
                            
    # print(result_graph)
    
    # with open("result/result_graphs_alledges_video02.pkl", "wb") as fw:
    # with open("result/result_graphs_alledges_epoch13_video08.pkl", "wb") as fw:
    # with open("result/result_graphs_alledges_layer08_video08.pkl", "wb") as fw:
    # with open("result/1217/vid08_1217_from_db.pkl", "wb") as fw:
    
    
    
    with open("result/0129/vid08_0129_from_db_overlapped.pkl", "wb") as fw:
        pickle.dump(result_graph, fw)
    
    print("@@@result@@@")
    print(result_graph)
    
    
    # # Final image rank
    # imgs = Counter(candidate_imgs)      
    # # img2idxDict: image metadata를 이용해 전체 dataset에서의 idx를 얻음
    # # idx2imgDict: datset 내 idx를 이용해 image metadata를 얻음
    # img2idxDict = {img: idx for img, idx in zip(candidate_imgs, candidate_imgs_idx)}
    # idx2imgDict = {idx:img  for img, idx in zip(candidate_imgs, candidate_imgs_idx)}
    
    # # 후보 군에서 가장 많이 언급된 이름 추출하고 
    # candidate_imgs = list(set('_'.join(item.split('_')) for item in candidate_imgs)) # videoId_fId
    # sorted_data = sorted(candidate_imgs, key=lambda x: (-candidate_imgs.count(x), x))
    # candidate_imgs = list(set(sorted_data)) #



def main():
    parser = argparse.ArgumentParser(description='embedding arguments')

    utils.parse_optimizer(parser)
    parse_encoder(parser)
    args = parser.parse_args()

    feature_extract(args)


if __name__ == "__main__":
    torch.set_printoptions(precision=20)
    main()

