from source import db
from flask import request, make_response, jsonify
from source.main.model.chat1vs1 import Chat1vs1
from source.main.model.relationship import Relationship
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import label, text


def chat1vs1(id):
    if (request.method=="GET"):
        try:
            chat = db.session.execute(text(
                            'Select * from users inner join chat1vs1 on users.id= chat1vs1.idReceive'))
            data=[]
            for row in chat:
                view_chat = {}
                view_chat["idSend"] = row.idSend
                view_chat['idReceive'] = row.idReceive
                view_chat["name"] = row.name
                view_chat['text'] = row.text
                view_chat['state'] = row.state
                view_chat['sendAt'] = row.sendAt
                data.append(view_chat)
            return {'state': 200, 'data': data} 
        except Exception as e:
            print(e)
            return make_response(jsonify({'status': 400, 'message': 'Request fail. Please try again'}), 400)
    if (request.method=="POST"):
            json = request.json         
            print(json)
            print(json['sendAt'])
            try:
                sentAt_time = datetime.strptime(
                                            json['sendAt'], '%d/%m/%Y %H:%M %p %z')
                print(json['content'])                
                newchat1vs1=Chat1vs1(sendAt=sentAt_time,idReceive=id,text=json['content'])               
                print("loi o ghep su kien")
                if (json['idSend']):
                    newchat1vs1.idSend=json['idSend']
                db.session.add(newchat1vs1)
                db.session.commit()
                chat_parse = {}
                chat_parse["id"] = newchat1vs1.id
                chat_parse["idSend"] = newchat1vs1.idSend
                chat_parse['idReceive']=newchat1vs1.idReceive
                chat_parse['content'] = newchat1vs1.text
                chat_parse['sendAt'] = str(newchat1vs1.sendAt)
                return {'status': 200, 'message': chat_parse}
            except:
                return make_response(jsonify({'status': 300, 'message': 'Sonpipi Request fail. Please try again'}), 300)
    if request.method=="DELETE":
        pass
def blockchat(id):
    if (request.method=="GET"):
        try:
            chat = db.session.execute(text(
                            'Select * from users inner join relationship on users.id= relationship.idReceive'))
            data=[]
            for row in chat:
                view_chat = {}
                view_chat["idSend"] = row.idSend
                view_chat["idReceive"] = row.idReceive
                view_chat["relationship"] = row.relation
                data.append(view_chat)
            return {'state': 200, 'data': data} 
        except Exception as e:
            print(e)
            return make_response(jsonify({'status': 400, 'message': 'Request fail. Please try again'}), 400)
    if (request.method=="POST"):
            json = request.json  # Get JSON data from the request
            try:
                # Try to find an existing relationship in the database based on certain conditions
                user1 = Relationship.query.filter(
                    (Relationship.idSend == id) & (Relationship.idReceive == json['idReceive'])).first()
                user2 = Relationship.query.filter(
                    (Relationship.idReceive == id) & (Relationship.idSend == json['idReceive'])).first()
                if user1 or user2:
                    # If a relationship exists, return its status
                    return {'status': 200, 'relation is': user1.relation}
                else:
                    # If no relationship exists, create a new one with relation set to True
                    new_relation1 = Relationship(idSend=id, idReceive=json['idReceive'], relation=True)
                    new_relation2 = Relationship(idReceive=id, idSend=json['idReceive'], relation=True)
                    db.session.add(new_relation1)
                    db.session.add(new_relation2)
                    db.session.commit()
                    
                    # Prepare a response message
                    chat_parse = {
                        "id": new_relation1.id,
                        "idSend": new_relation1.idSend,
                        "idReceive": new_relation1.idReceive,
                        "relation": new_relation1.relation
                    }
                    
                    # Return a JSON response with the newly created relationship data
                    return {'status': 200, 'message': chat_parse}
            except Exception as e:
                # Handle exceptions, e.g., database errors
                print(e)
                return make_response(jsonify({'status': 300, 'message': 'Sonpipi Request fail. Please try again'}), 300)
    if (request.method=="PATCH"):
            json = request.json  # Get JSON data from the request
            try:
                # Try to find an existing relationship in the database based on certain conditions
                user = Relationship.query.filter(
                    (Relationship.idSend == id) & (Relationship.idReceive == json['idReceive'])
                ).first()
                if user:
                    # If a relationship exists, return its status
                    user.relation = json["relation"]
                    db.session.commit()
                    chat_parse = {
                        "id": user.id,
                        "idSend": user.idSend,
                        "idReceive": user.idReceive,
                        "relation": user.relation
                    }
                    return {'status': 200, 'message': chat_parse}
                else:
                    return {'status': 200, 'message':"no relationship"}
            except Exception as e:
                # Handle exceptions, e.g., database errors
                print(e)
                return make_response(jsonify({'status': 300, 'message': 'Sonpipi Request fail. Please try again'}), 300)
def statemessage(id):
    try:
        if(request.method=="POST"):
            message=Chat1vs1.query.filter( Chat1vs1.id == id).first()
            message.state="seen"
            db.session.commit()
            return"state message change 'seen'"
    except Exception as e:
        print(e)
        return make_response(jsonify({'status': 300, 'message': 'Sonpipi Request fail. Please try again'}), 300)