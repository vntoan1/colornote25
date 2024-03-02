from source import db
from flask import request, make_response, jsonify
from source.main.model.chatUnknowns import ChatUnknowns
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import label

def handleChatUnknowns(param):
    if request.method=="GET":
       # Truy vấn để lấy tin nhắn cuối cùng cho mỗi idSend của idReceiver cụ thể
        subquery = db.session.query(ChatUnknowns.idSend, func.max(ChatUnknowns.sendAt).label('max_sendAt')).filter(ChatUnknowns.idReceive == param).group_by(ChatUnknowns.idSend).subquery()
        query = db.session.query(ChatUnknowns).join(subquery, (ChatUnknowns.idSend == subquery.c.idSend) & (ChatUnknowns.sendAt == subquery.c.max_sendAt))

        # Lấy kết quả của truy vấn
        latest_messages = query.all()
        res={}
        idSend=""
        for chat in latest_messages:
            chat_parse = {}
            chat_parse["id"] = chat.idMes
            idSend=chat.idSend
            chat_parse["idSend"] = chat.idSend
            chat_parse['idReceive']=chat.idReceive
            chat_parse['status']=chat.status
            chat_parse['lastest']={
                'content' : chat.text,
                'sendAt' : str(chat.sendAt)
            }            
            res[idSend]=chat_parse
        return  res
    if request.method=="DELETE":
        pass
def handleMessages(id):
    if (request.method == 'GET'):
        chats = ChatUnknowns.query.filter_by(
            idSend=id).order_by(ChatUnknowns.sendAt.desc()).all()
        data = []
        for chat in chats:
            chat_parse = {}
            chat_parse["id"] = chat.idMes
            chat_parse["idSend"] = chat.idSend
            chat_parse['idReceive']=chat.idReceive
            chat_parse['content'] = chat.text
            chat_parse['sendAt'] = str(chat.sendAt)
            data.append(chat_parse)
        return {'status': 200, 'data': data}
    if (request.method=="POST"):
        #    return {"hehe":"khong"}
            content = request.get_json()
            print(content)
            json = request.json
            
            print(json)
            print(json['sendAt'])
            try:
                print(json['sendAt'])
                sentAt_time = datetime.strptime(
                    json['sendAt'], "%d/%m/%Y %H:%M %p %z") #'01/03/2024 10:15 AM +07:00'
                #2023-07-12 14:12:06
                print(sentAt_time)                #>>> my_time = time.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
                chatUnknowns=ChatUnknowns(sendAt=sentAt_time,idReceive=id,text=json['content'])               
                if (json['idSend']):
                    chatUnknowns.idSend=json['idSend']
                db.session.add(chatUnknowns)
                db.session.commit()
                chat_parse = {}
                chat_parse["id"] = chatUnknowns.idMes
                chat_parse["idSend"] = chatUnknowns.idSend
                chat_parse['idReceive']=chatUnknowns.idReceive
                chat_parse['content'] = chatUnknowns.text
                chat_parse['sendAt'] = str(chatUnknowns.sendAt)
                return {'status': 200, 'message': chat_parse}
            except Exception as e:
            # Log the error message
                print("SQL Error:", str(e))
                return {'status': 500, 'message': str(e)}