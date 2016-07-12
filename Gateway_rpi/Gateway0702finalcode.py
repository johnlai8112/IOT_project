# GateWay
# socket 
# http://hhtucode.blogspot.tw/2013/03/python-simple-socket-server.html
# mqtt
# http://rocksaying.tw/archives/2016/MQTT-3-Python-clients.html
# -*- coding: utf8 -*-

import paho.mqtt.client as mqtt
import threading
import json
import socket

BrokerIP = "iot.eclipse.org"
BrokerPort = 1883
IoT_server_TopicName = "IOTSV/REG"
IPaddress = "172.20.10.5"
port = 8880

# Gateway名稱 
GatewayName = "NODEGW_01"

# 將全域共用變數用lock去包裝起來 讓兩個thread 不會去搶到
lock = threading.Lock()

# 第一個位置擺放訊息字串, 第二個位置擺放數字供程式判別是否做動作

Nodes = [  ]
MSG_FS = ["", 0,"",0,""]
MSG_Node = ["", 0,"",0,""]
MSG_string = ["", 0,"",0,""]

# 註冊時送給IoT Server的字串轉成Json格式
Registor_Gateway = {'Node': "NODE_GW01", 'Control': 'NODE_REG', 'NodeFunctions': ['Node01'], 'Functions': ['Node01'], 'Source': "NODE_GW01", 'NodeLBType': 'DType', 'NodeMAC': "AA-BB-CC-DD-EE-FF"}
Registor_Gateway_Json =  json.dumps(Registor_Gateway)

# 啟動程式時, 先註冊自己的資訊給IoT_Server
MqttConnect = mqtt.Client()

# 程式分成兩個不同的thread在跑, 一個mqtt為第二個thread 另一個wifi socket跑在主要thread中 以達到同步執行的效果
def thread_of_functions ():

		thread_mqtt = objectoriented_of_mqtt()
	   thread_mqtt.start()
		MqttConnect.connect(BrokerIP, BrokerPort)
		MqttConnect.publish(IoT_server_TopicName, Registor_Gateway_Json)
		MqttConnect.loop(2)
		thread_wifi = thread_socket()
		#thread_wifi.start()

# 在socket機制中, 定義為server端, 負責socket的資料接收然後mqtt送出
def thread_socket():
        # 會使用到的全域變數
        global MSG_FS
        global MSG_Node
        global GatewayName
        # 定義為外部網路(可由不同網域連線), 接收訊息為確保可以收到為基準(TCP)
        sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        print (123)
        #定義自身的ip位址以及port讓其他人連線近來
        sock.bind ((IPaddress, port))
        # 有多少device可以連接到server
        sock.listen(5)      
        # socket開始偵測訊息
        while 1 :
                # socket 接收訊息  會接收到傳送端的ip位址以及對應的port號
                clientsocket, ip= sock.accept()
                # 放置client端ip位址的list
                client = []
                if ip not in client :
                    client.append(ip)
                print(client)
                try : 
                    if ip == client[0] :
                            lock.acquire()
                            M = clientsocket.recv(1024)
                            MSG_Node[0] = int(M)
                            MSG_Node[1] = 1
                            print (MSG_Node[0])
                            lock.release()

                    if ip == client[1]:
                            lock.acquire()
                            MS = clientsocket.recv(1024)
                            MSG_Node[2] = int(MS)
                            MSG_Node[3] = 1
                            print (MSG_Node[2])
                            lock.release()
                except :
                    print ("rv error")
                # 如果FS有資料要送給指定Node時, 將資料透過socket傳送出去
                
                if (MSG_FS[1] != 0):
                        # 先將之前的資料放進Json格式中以免出錯
                        FS_Json = json.loads(json.dumps(MSG_FS[0]))
                        try :
                            # 如果是node_1 要接收到資料時
                            if (FS_Json["Target"] == "Node_01") :
                                    st = 'h'
                                    clientsocket.sendto(st , client[0][0])
                                    clientsocket.close()
                                    MSG_FS[1] = 0
                            # 如果是node_2 要接收到資料時
                            elif FS_Json["Target"] == "Node_02" :
                                    stop = 'h'
                                    clientsocket.sendto(stop , client[1][0])
                                    clientsocket.close()
                                    MSG_FS[1] = 0    
                        except :
                            print('exception of send heart beat error to client')
                # node_ 1 如果有資料要上傳給FS , 檢查MSG_Node裡面是否有資訊, 將他的訊息publish在mqtt指定的topic中
                if (MSG_Node[1] != 0) :
                        # 先定義資料上傳的Json格式
                        Node01_from_String = { "Node" : "Node_GW01",  "Control" : "Sensor_Data", "Function" : "N2F", "Type_of_MSG": "Normal", "Data" : [{"Heart_Beat": 0, "Bump" : 0}], "Source" : "Node_GW01"}
                        NFS = json.dumps(Node01_from_String)
                        N_F_S = json.loads(NFS)
                        # 判斷底下node上傳的資料是不是碰撞事件
                        if MSG_Node[0] < 0 :
                                string = 'b'
                                clientsocket.send(string)
                                clientsocket.close()
                                N_F_S['Data'][1]['Bump'] = 1
                                N_F_S['Type_of_MSG'] = "Emergency"
                        # 不然就是心跳的訊息                        		
                        else :
                            N_F_S['Data'][0]['Heart_Beat']= MSG_Node[0]
                        # 將資料透過mqtt方式傳送給雲端
                        MSG_to_FS = json.dumps(N_F_S)
                        MqttConnect = mqtt.Client()
                        MqttConnect.connect(BrokerIP, BrokerPort, 60)
                        MqttConnect.publish(GatewayName, MSG_to_FS)
                        MqttConnect.loop(2)
                        MSG_Node[1] = 0
                # node_ 2 如果有資料要上傳給FS , 檢查MSG_Node裡面是否有資訊, 將他的訊息publish在mqtt指定的topic中
                if (MSG_Node[3] != 0) :
                        Node02_from_String = { "Node" : "Node_02",  "Control" : "Sensor_Data", "Function" : "N2F", "Type_of_MSG": "Normal", "Data" : [{"Heart_Beat": 0, "Bump" : 0}], "Source" : "GW_01"}
                        NFS2 = json.dumps(Node02_from_String)
                        N_F_S2 = json.loads(NFS2)
                        if MSG_Node[2] < 0 :
                                string = 'b'
                                clientsocket.send(string)
                                clientsocket.close()
                                N_F_S2['Data'][1]['Bump'] = 1
                                N_F_S2[Type_of_MSG] = "Emergency"
                        else :
                            N_F_S2['Data'][0]['Heart_Beat']= MSG_Node[0]
                        MSG2_to_FS = json.dumps(N_F_S2)
                        MqttConnect = mqtt.Client()
                        MqttConnect.connect(BrokerIP, BrokerPort, 60)
                        MqttConnect.publish(GatewayName, MSG2_to_FS)
                        MqttConnect.loop(2)

                        MSG_Node[3] = 0





# 一個物件導向的thread專門處理MQTT相關
class objectoriented_of_mqtt(threading.Thread) :
	
        def __init__(self):
                threading.Thread.__init__(self)

        def run(self):
                
                global GatewayName
                global MSG_FS
                global MSG_string
        

		
                print (1)
                MqttConnect = mqtt.Client("GatewayName")
		

                def on_connect(client, userdata, flags, rc):
                    # mqtt連線時追蹤的頻道
                        MqttConnect.subscribe(GatewayName)
                        MqttConnect.subscribe("IOTSV/REG")
                    
                def on_message(client, userdata, msg):
                    # 接收mqtt資訊的處理
                        try :
                                if (msg.payload != "") :
                                        print  (msg.payload)
                                        J = msg.payload.decode(encoding= 'UTF-8')
                                        Json = json.loads(J)
                                        print (Json)
# 在收到訊息時, 判定內容是不是緊急事件, 如果是緊急事件, 將他透過網路傳給下面的device
                                        lock.acquire()
                                        MSG_FS[0] = Json
                                        MSG_FS[1] = 1
                                        lock.release()
                                        
                        except :
                                print ("Mqtt_rv_error")
                MqttConnect = mqtt.Client()
                MqttConnect.on_connect = on_connect
                MqttConnect.on_message = on_message
                MqttConnect.connect(BrokerIP, BrokerPort, 60)
                MqttConnect.loop_forever()

thread_of_functions()
