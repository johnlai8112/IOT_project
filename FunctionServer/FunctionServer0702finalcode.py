# Function Server

import paho.mqtt.client as mqtt
import threading
import json
#import MySQLdb
import pymysql
import time     
BrokerIP = "iot.eclipse.org"
BrokerPort = 1883
Reg_TopicName ="IOTSV/REG"
class PublisherManager():
    def MQTT_PublishMessage(self, topicName, message):
        print("[INFO] MQTT Publishing message to topic: %s, Message:%s" % (topicName, message))
        
        MqttConnect = mqtt.Client()
        MqttConnect.connect(BrokerIP, BrokerPort, 60)
        MqttConnect.publish(topicName, message)
        MqttConnect.loop(2)


count_node_1 = 0
count_node_2 = 0 
count_node_3 = 0 

Reg_TopicName = ""
FS_name = "FS_1st_group"

# 有更新 6/24   *********************
# 先註冊FS相關資訊給IoT_Server

Registor_FS = { "FunctionServer": "FS_1st_group", "Control": "FS_REG", "Function": "M2M", "MappingNodes" : ['NODE_GW01','NODE_GW02'], "Source": "FS_1st_group" , "FSIP" : "10.0.0.1"}

Registor_FS_Json =  json.dumps(Registor_FS)

publisherManger = PublisherManager()
publisherManger.MQTT_PublishMessage("IOTSV/REG", Registor_FS_Json)



# 紀錄每個device的頻道以及訊息 
# RuleID, InputNode, InputIO, OutputNode, OutputIO, TargetValueOverride
_g_M2MRulesMappingList = [{"RuleID": "1", "InputNode": "NODE-01", "InputIO": "SW1",
                           "OutputNode": "NODE-02", "OutputIO": "LED3", "TargetValueOverride": "EQU"},

                          {"RuleID": "2", "InputNode": "NODE-01", "InputIO": "SW1",
                           "OutputNode": "NODE-02", "OutputIO": "LED4", "TargetValueOverride": "0"},

                          {"RuleID": "3", "InputNode": "NODE-02", "InputIO": "SW2",
                           "OutputNode": "NODE-01", "OutputIO": "LED2", "TargetValueOverride": "1"},

                          {"RuleID": "4", "InputNode": "NODE-01", "InputIO": "SW1",
                           "OutputNode": "NODE-03", "OutputIO": "LED1", "TargetValueOverride": "EQU"},

                           {"RuleID": "5", "InputNode": "NODE-03", "InputIO": "SW1",
                           "OutputNode": "NODE-01", "OutputIO": "LED1", "TargetValueOverride": "EQU"}
                          ]

# 判定IoT_server要求追蹤頻道的機制
class FunctionServerMappingRules():
    def __init__(self):
        self.jsonObj = class_M2MFS_Obj.JSON_REPTOPICLIST()

    def replyM2MTopicToNode(self, topicName, NodeName):
        self.jsonObj.Gateway = NodeName
        IsNodeHaveM2MMappingRules = False
        readyToReplyTopics = []

        for SingleM2MMappingRule in _g_M2MRulesMappingList:

            if (SingleM2MMappingRule["OutputNode"] == NodeName):
                readyToReplyTopics.append(SingleM2MMappingRule)

        if (len(readyToReplyTopics) > 0):
            IsNodeHaveM2MMappingRules = True
            for SingleM2MMappingRule in readyToReplyTopics:
                #### ASSIGN TO M2M FS ####
                self.SubscribeTopics = SubscribeTopicsObj()
                self.SubscribeTopics.TopicName = SingleM2MMappingRule["InputNode"] + \
                                                 "/" + SingleM2MMappingRule["InputIO"]  # FS1
                self.SubscribeTopics.Node = SingleM2MMappingRule["OutputNode"]  # M2M
                self.SubscribeTopics.Target = SingleM2MMappingRule["OutputIO"]
                self.SubscribeTopics.TargetValueOverride = SingleM2MMappingRule["TargetValueOverride"]

                self.jsonObj.SubscribeTopics.append(self.SubscribeTopics)

        else:
            IsNodeHaveM2MMappingRules = False

        jsonstring = self.jsonObj.to_JSON()

        print("[Rules] REPTOPICLIST Send to topic:%s" % (topicName))

        pm = PublisherManager()
        pm.MQTT_PublishMessage(topicName, jsonstring)



    def replyM2MRulesAll(self, topicName):
        self.jsonObj = JSON_M2MRULE()

        for SingleM2MMappingRule in _g_M2MRulesMappingList:
            self.Rule = RuleObj()
            self.Rule.RuleID = SingleM2MMappingRule["RuleID"]
            self.Rule.InputNode = SingleM2MMappingRule["InputNode"]
            self.Rule.InputIO = SingleM2MMappingRule["InputIO"]
            self.Rule.OutputNode = SingleM2MMappingRule["OutputNode"]
            self.Rule.OutputIO = SingleM2MMappingRule["OutputIO"]
            self.Rule.TargetValueOverride = SingleM2MMappingRule["TargetValueOverride"]
            self.jsonObj.Rules.append(self.Rule)

        jsonstring = self.jsonObj.to_JSON()

        print("[Rules] REPRULE Send to topic:%s" % (topicName))

        pm = PublisherManager()
        pm.MQTT_PublishMessage(topicName, jsonstring)

    def AddM2MRule(self, RuleObjs):
        print("[Rules] ADDRULE start %s" % (RuleObjs))

        NotifyNodes = []

        for SingleM2MMappingRule in RuleObjs:
            NotifyNodes.append(SingleM2MMappingRule["OutputNode"])
            _g_M2MRulesMappingList.append(SingleM2MMappingRule)

        self.ModifyRePublishToNode(NotifyNodes)
        print("[Rules] ADDRULE end!")

    def UpdateM2MRule(self, RuleObjs):
        print("[Rules] UPDATERULE start %s" % (RuleObjs))

        NotifyNodes = []

        for SingleM2MMappingRule in RuleObjs:
            for updateRule in _g_M2MRulesMappingList:
                if (updateRule["RuleID"] == SingleM2MMappingRule["RuleID"]):
                    # 蠻怪的，陣列內dict變動，list內卻沒有跟著變??，只好砍掉重新加入
                    NotifyNodes.append(updateRule["OutputNode"])
                    _g_M2MRulesMappingList.remove(updateRule)
                    _g_M2MRulesMappingList.append(SingleM2MMappingRule.copy())
                    NotifyNodes.append(SingleM2MMappingRule["OutputNode"])

        self.ModifyRePublishToNode(NotifyNodes)
        print("[Rules] UPDATERULE end!" )

    def DelM2MRule(self, RuleObjs):
        print("[Rules] DELRULE start %s" % (RuleObjs))

        NotifyNodes = []

        for SingleM2MMappingRule in RuleObjs:
            for delRule in _g_M2MRulesMappingList:
                if (delRule["RuleID"] == SingleM2MMappingRule["RuleID"]):
                    NotifyNodes.append(delRule["OutputNode"])
                    _g_M2MRulesMappingList.remove(delRule)

        self.ModifyRePublishToNode(NotifyNodes)
        print(bcolors.OKGREEN + "[Rules] DELRULE end!" + bcolors.ENDC)

    def ModifyRePublishToNode(self, NotifyNodes):
        print("[Rules] Republish New M2M Rules for relate Node." )
        NotifyNodes = list(set(NotifyNodes))
        for Nodes in NotifyNodes:
            self.replyM2MRulesAll(Nodes)

class JSON_REPTOPICLIST():
    ###因為是自訂類別，所以要用這種方式轉出
    ## http://stackoverflow.com/questions/3768895/python-how-to-make-a-class-json-serializable
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)  # , indent=4) 要indent在uncommit

    def __init__(self):
        self.Source = M2MFunctionServer._g_cst_FSUUID
        self.Gateway = ""
        self.Control = "M2M_REPTOPICLIST"
        self.SubscribeTopics = []  # SubscribeTopicsObj


class SubscribeTopicsObj:
    def __init__(self):
        self.TopicName = ""
        self.Node = ""
        self.Target = ""
        self.TargetValueOverride = ""


###############################################################

class JSON_M2MRULE():
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)  # , indent=4) 要indent在uncommit

    def __init__(self):
        self.Source = M2MFunctionServer._g_cst_FSUUID
        self.Control = "M2M_REPRULE"
        self.Rules = []


class RuleObj:
    def __init__(self):
        self.RuleID = ""
        self.InputNode = ""
        self.InputIO = ""
        self.OutputNode = ""
        self.OutputIO = ""
        self.TargetValueOverride = ""

# 一個物件導向的thread專門處理MQTT相關
class objectoriented_of_mqtt(threading.Thread) :
    
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self): 
        
        global FS_name
        global count_node_1
        global count_node_2
        global count_node_3

    

        MqttConnect = mqtt.Client()
        
        # 追蹤自己名稱的頻道
        def on_connect(client, userdata, flags, rc):

            MqttConnect.subscribe(FS_name)
        # 接收mqtt資訊的機制
        def on_message(client, userdata, msg):
            if (msg.payload != "") :
                J = msg.payload.decode(encoding= 'UTF-8')
                Json = json.loads(J)

                if (Json['Source'] != FS_name):
                    if (Json["Control"] == "M2M_REQTOPICLIST"):
                            m2mfsmrules = FunctionServerMappingRules()
                            time.sleep(1)
                            m2mfsmrules.replyM2MTopicToNode("FS_1st_group", Json["Node"])
                    elif (Json["Control"] == "M2M_GETRULE"):
                            m2mfsmrules = FunctionServerMappingRules()
                            m2mfsmrules.replyM2MRulesAll("FS_1st_group")
                    elif (Json["Control"] == "M2M_ADDRULE"):
                            m2mfsmrules = FunctionServerMappingRules()
                            m2mfsmrules.AddM2MRule(Json["Rules"])
                    elif (Json["Control"] == "M2M_UPDATERULE"):
                            m2mfsmrules = FunctionServerMappingRules()
                            m2mfsmrules.UpdateM2MRule(Json["Rules"])
                    elif (Json["Control"] == "M2M_DELRULE"):
                            m2mfsmrules = FunctionServerMappingRules()
                            m2mfsmrules.DelM2MRule(Json["Rules"])

                # 在收到訊息時, 判定內容是不是要給FS的, 如果是, 用mysql的指令寫入
                if Json["Control"] == "Sensor_Data" :
                # 心跳偵測回傳值連續超出或低於臨界值時, 將自動回傳訊息給node端
                    threshold_down = 70
                    threshold_up = 120
                    threshold_shutdown = 5
                    if Json["Node"] == "Node_GW01" :
                            # 如果心跳值小於70或是大於120
                            if ( int(Json["Data"][0]["Heart_Beat"])< threshold_down ) or ( int(Json["Data"][0]["Heart_Beat"])> threshold_up ):
                                    count_node_1 += 1
                                    if (count_node_1 == threshold_shutdown) :
                                        str_to_node =  { "Target" : "Node_GW01",  "Control" : "FS_Command", "Function" : "F2N", "Type_of_MSG": "Emergency" , "Data": "Shut_Down" , "Source" : "FS_1st_group"}
                                        str_to_node_Json =  json.dumps(str_to_node)
                                        publisherManger =PublisherManager()
                                        publisherManger.MQTT_PublishMessage(FS_name, str_to_node_Json)
                                        # 將心跳問題上傳到DB中
                                        db = pymysql.connect("localhost","root","","mydb" )
                                        # prepare a cursor object using cursor() method
                                        cursor = db.cursor()
                                        # Prepare SQL query to INSERT a record into the database.
                                        # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                        heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                        heart_beat=int(Json["Data"][0]["Heart_Beat"])
                                        heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
                                                    VALUES (null,'%s','%s','%d','true')"""%(heart_datetime,Json["Node"],heart_beat)
                                        try:
                                           # Execute the SQL command
                                           cursor.execute(heart_sql)
                                           # Commit your changes in the database
                                           db.commit()
                                        except:
                                           # Rollback in case there is any error
                                           db.rollback()
                                        # disconnect from server
                                        db.close()

                            elif ( int(Json["Data"][0]["Heart_Beat"])> threshold_down ) or ( int(Json["Data"][0]["Heart_Beat"])< threshold_up ):
                                    count_node_1 =0
                                    print("Normal")    
                                    #沒有心跳問題 一樣上傳心跳數值  唯一差別event的判定為false ==>代表沒有發生異常
                                    db = pymysql.connect("localhost","root","","mydb" )
                                    # prepare a cursor object using cursor() method
                                    cursor = db.cursor()
                                    # Prepare SQL query to INSERT a record into the database.
                                    # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)                               
                                    heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                    heart_beat=int(Json["Data"][0]["Heart_Beat"])
                                    heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
                                                    VALUES (null,'%s','%s','%d','false')"""%(heart_datetime,Json["Node"],heart_beat)                 
                                    try:
                                        # Execute the SQL command
                                        cursor.execute(heart_sql)
                                        # Commit your changes in the database
                                        db.commit()
                                    except:
                                        # Rollback in case there is any error
                                        db.rollback()
                                    # disconnect from server
                                    db.close()
                            # 發生碰撞

                            elif (int(Json["Data"][0]["Bump"]) == 1 ):
                                db = pymysql.connect("localhost","root","","mydb" )
                                # prepare a cursor object using cursor() method
                                cursor = db.cursor()
                                # Prepare SQL query to INSERT a record into the database.
                                # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                car_datetime=time.strftime('%Y-%m-%d %H:%M:%S')

                                car_sql = """INSERT INTO CAR_EVENT(eprikey,edate,nodename)
                                            VALUES (null,'%s','%s')"""%(car_datetime,Json["Node"])
                                try:
                                    # Execute the SQL command
                                    cursor.execute(car_sql)
                                    # Commit your changes in the database
                                    db.commit()
                                except:
                                # Rollback in case there is any error
                                    db.rollback()
                                # disconnect from server
                                db.close()

            
                    if Json["Node"] == "Node_GW02" :

                            if ( int(Json["Data"][0]["Heart_Beat"])< threshold_down ) or ( int(Json["Data"][0]["Heart_Beat"])> threshold_up ):
                                    count_node_2 += 1
                                    if (count_node_2 == threshold_shutdown) :
                                        str_to_node =  { "Target" : "Node_02",  "Control" : "FS_Command", "Function" : "F2N", "Type_of_MSG": "Emergency" , "Data": "Shut_Down" , "Source" : "FS_1st_group"}
                                        str_to_node_Json =  json.dumps(str_to_node)
                                        publisherManger = PublisherManager()
                                        publisherManger.MQTT_PublishMessage(FS_name, str_to_node_Json)
                                        # 將心跳運題上傳到DB中
                                        db = pymysql.connect("localhost","root","","mydb" )
                                        # prepare a cursor object using cursor() method
                                        cursor = db.cursor()
                                        # Prepare SQL query to INSERT a record into the database.
                                        # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                        heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                        heart_count=int(Json["Data"][0]["Heart_Beat"])
                                        heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
                                                    VALUES (null,'%s','%s','%d','true')"""%(heart_datetime,Json["Node"],heart_beat)
                                        try:
                                           # Execute the SQL command
                                           cursor.execute(heart_sql)
                                           # Commit your changes in the database
                                           db.commit()
                                        except:
                                           # Rollback in case there is any error
                                           db.rollback()
                                        # disconnect from server
                                        db.close()

                            elif ( int(Json["Data"][0]["Heart_Beat"])> threshold_down ) or ( int(Json["Data"][0]["Heart_Beat"])< threshold_up ):
                                    count_node_2 =0

                                    #沒有心跳問題 一樣上傳心跳數值  唯一差別event的判定為false ==>代表沒有發生異常
                                    db = pymysql.connect("localhost","root","","mydb" )
                                    # prepare a cursor object using cursor() method
                                    cursor = db.cursor()
                                    # Prepare SQL query to INSERT a record into the database.
                                    # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                    heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                    heart_beat=int(Json["Data"][0]["Heart_Beat"])
                                    heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
                                                    VALUES (null,'%s','%s','%d','false')"""%(heart_datetime,Json["Node"],heart_beat)

                                    try:
                                        # Execute the SQL command
                                        cursor.execute(heart_sql)
                                        # Commit your changes in the database
                                        db.commit()
                                    except:
                                        # Rollback in case there is any error
                                        db.rollback()

                                    # disconnect from server
                                    db.close()
                            elif (int(Json["Data"][1]["Bump"]) == 1 ):
                                db = pymysql.connect("localhost","root","","mydb" )
                                # prepare a cursor object using cursor() method
                                cursor = db.cursor()
                                # Prepare SQL query to INSERT a record into the database.
                                # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                car_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                car_sql = """INSERT INTO CAR_EVENT(eprikey,edate,nodename)
                                            VALUES (null,'%s','%s')"""%(car_datetime,Json["Node"])

                                try:
                                    # Execute the SQL command
                                    cursor.execute(car_sql)
                                    # Commit your changes in the database
                                    db.commit()
                                except:
                                # Rollback in case there is any error
                                    db.rollback()
                                # disconnect from server
                                db.close()

                    if Json["Node"] == "Node_GW03" :

                            if ( int(Json["Data"][0]["Heart_Beat"])< threshold_down ) or ( int(Json["Data"][0]["Heart_Beat"])> threshold_up ):
                                    count_node_3 += 1
                                    if (count_node_3 == threshold_shutdown) :
                                        str_to_node =  { "Target" : "Node_03",  "Control" : "FS_Command", "Function" : "F2N", "Type_of_MSG": "Emergency" , "Data": "Shut_Down" , "Source" : "FS_1st_group"}
                                        str_to_node_Json =  json.dumps(str_to_node)
                                        publisherManger = PublisherManager()
                                        publisherManger.MQTT_PublishMessage(FS_name, str_to_node_Json)
                                        # 將心跳運題上傳到DB中
                                        db = pymysql.connect("localhost","root","","mydb" )
                                        # prepare a cursor object using cursor() method
                                        cursor = db.cursor()
                                        # Prepare SQL query to INSERT a record into the database.
                                        # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                        heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                        heart_count=int(Json["Data"][0]["Heart_Beat"])
                                        heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
                                                    VALUES (null,'%s','%s','%d','true')"""%(heart_datetime,Json["Node"],heart_beat)
                                        try:
                                           # Execute the SQL command
                                           cursor.execute(heart_sql)
                                           # Commit your changes in the database
                                           db.commit()
                                        except:
                                           # Rollback in case there is any error
                                           db.rollback()
                                        # disconnect from server
                                        db.close()



                            elif ( int(Json["Data"][0]["Heart_Beat"])> threshold_down ) or ( int(Json["Data"][0]["Heart_Beat"])< threshold_up ):
                                    count_node_3 = 0
                                    db = pymysql.connect("localhost","root","","mydb" )
                                    # prepare a cursor object using cursor() method
                                    cursor = db.cursor()
                                    # Prepare SQL query to INSERT a record into the database.
                                    # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                    heart_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                    heart_beat=int(Json["Data"][0]["Heart_Beat"])
                                    heart_sql = """INSERT INTO HEART_EVENT(hprikey,hdate,nodename,heartcount,event)
                                                    VALUES (null,'%s','%s','%d','false')"""%(heart_datetime,Json["Node"],heart_beat)

                                    try:
                                        # Execute the SQL command
                                        cursor.execute(heart_sql)
                                        # Commit your changes in the database
                                        db.commit()
                                    except:
                                        # Rollback in case there is any error
                                        db.rollback()

                                    # disconnect from server
                                    db.close()
                            elif (int(Json["Data"][1]["Bump"]) == 1 ):
                                db = pymysql.connect("localhost","root","","mydb" )
                                # prepare a cursor object using cursor() method
                                cursor = db.cursor()
                                # Prepare SQL query to INSERT a record into the database.
                                # 數值在DB的欄位  對應的參數值 (要討論要有多少個參數)
                                car_datetime=time.strftime('%Y-%m-%d %H:%M:%S')
                                car_sql = """INSERT INTO CAR_EVENT(eprikey,edate,nodename)
                                            VALUES (null,'%s','%s')"""%(car_datetime,Json["Node"])

                                try:
                                    # Execute the SQL command
                                    cursor.execute(car_sql)
                                    # Commit your changes in the database
                                    db.commit()
                                except:
                                # Rollback in case there is any error
                                    db.rollback()

                                # disconnect from server
                                db.close()
                        



                # 上傳到 server端

        # mqtt接收IoT_ server或是gateway送出的訊息作運算
        MqttConnect = mqtt.Client()
        MqttConnect.on_connect = on_connect
        MqttConnect.on_message = on_message
        MqttConnect.connect(BrokerIP, BrokerPort, 60)
        MqttConnect.loop_forever()

while True :

        thread_mqtt = objectoriented_of_mqtt()
        thread_mqtt.start()
        thread_mqtt.join()
  

