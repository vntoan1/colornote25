from source import db
from flask import request, make_response, jsonify
from source.main.model.notes import Notes
from source.main.model.users import Users
from source.main.model.comments import Comments
from source.main.model import *
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import label
from flask_jwt_extended import jwt_required
from sqlalchemy import text, and_
import jwt

def postCommentnotes(idNote):
    if (request.method=="POST"):         
            try:
                json = request.json           
                print(json)
                print(json['sendAt'])
                sentAt_time = datetime.strptime( json['sendAt'], '%Y-%m-%dT%H:%M:%S.%f%z')
                print(json['content'])
                comments=Comments(sendAt=sentAt_time,idNote=json['idNote'],text=json['content'],parent_id=json['parent_id'])
                print("loi o ghep su kien")                
                if (json['idUser']):
                    comments.idUser=json['idUser']
                # print(comments)
                db.session.add(comments)
                db.session.commit()
                comments_users = {}
                comments_users["id"] = comments.id
                comments_users["idNote"] = comments.idNote
                comments_users["idUser"] = comments.idUser
                comments_users["parent_id"] = comments.parent_id
                comments_users['content']=comments.text
                comments_users['sendAt'] = str(comments.sendAt)
                return {'status': 200, 'message': comments_users}
            except Exception as e :
                print(e)
                return make_response(jsonify({'status': 300, 'message': str(e)}), 300)
def getCommentnotes(idNote):
    if (request.method == 'GET'):
        try:         
            data = []
            query = text('SELECT * FROM ((comments AS c INNER JOIN users AS u ON c.idUser = u.id) INNER JOIN notes AS n ON c.idNote = n.idNote) WHERE c.idNote = :idNote')            
            tv = db.session.execute(query, {'idNote': idNote})
            for getcomment in tv:
                comment_parse = {}
                comment_parse["id"] = getcomment.id
                comment_parse["idUser"] = getcomment.idUser
                comment_parse["idNote"] = getcomment.idNote
                comment_parse["parent_id"] = getcomment.parent_id
                comment_parse["avt"] = getcomment.linkAvatar
                comment_parse["user_name"] = getcomment.user_name
                comment_parse['content'] = getcomment.text
                comment_parse['sendAt'] = str(getcomment.sendAt)
                data.append(comment_parse)
            return {'status': 200, 'data': data}
        except Exception as e :
                print(e)
                return make_response(jsonify({'status': 300, 'message': str(e)}), 300)