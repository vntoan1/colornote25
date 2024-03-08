from source import app, mail
from source.main.function.handleUsers import handleUsers
from source.main.function.handleUsers import getAllUser
from source.main.function.handleUsers import checkPasssword2
from source.main.function.handleUsers import createPass2
from source.main.function.handleUsers import get20LastestUser
from source.main.function.createUser import *
from source.main.function.loginUser import *
from source.main.function.loginUser import logout
from source.main.function.handleUsers import getProfile
from source.main.function.loginUser import stateLogin
from source.main.function.handleUsers import changeProfile
from source.main.function.handleUsers import searchUser
from source.main.function.handleUsers import searchnameUser
from source.main.function.handleUsers import *
from flask import jsonify, make_response, request, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_mail import *
from sqlalchemy import or_
from source.main.model.users import Users
from postmarker.core import PostmarkClient
import random

# from source.main.function.resetPassword import forgotPasswork
# from source.main.function.resetPassword import confirmforgotPassword
# from source.main.function.resetPassword import fogot

from passlib.hash import pbkdf2_sha256

client = PostmarkClient(server_token=app.config['POSTMARK_API'])

s = URLSafeTimedSerializer(app.config["SECRET_KEY"])

app.add_url_rule('/user/<string:param>', methods=['PATCH', 'POST'], view_func=handleUsers)
app.add_url_rule('/allUsers/<string:who>', methods=['GET'], view_func=getAllUser)
app.add_url_rule('/lastUser', methods=['GET'], view_func=get20LastestUser)
app.add_url_rule('/login', methods=['POST', ], view_func=loginUser)
app.add_url_rule('/logout/<string:id>', methods=['POST'], view_func=logout)

app.add_url_rule('/create-pass-2/<string:who>', methods=['POST'], view_func=createPass2)
app.add_url_rule('/open-pass-2/<string:who>', methods=['POST'], view_func=checkPasssword2)
app.add_url_rule('/profile/<string:who>', methods=['GET'], view_func=getProfile)
app.add_url_rule('/profile/change_Profile/<string:id>', methods=['PATCH'], view_func=changeProfile)
app.add_url_rule('/profile/patch_profile/<string:id_user>', methods=['PATCH'], view_func=patch_profile)
app.add_url_rule('/login', methods=['GET'], view_func=stateLogin)

app.add_url_rule('/profiles_search', methods=['GET'], view_func=searchUser)
app.add_url_rule('/profiles_search/user', methods=['GET'], view_func=searchnameUser)
app.add_url_rule('/resetPasswork/change', methods=['PATCH'], view_func=change)

app.add_url_rule('/deleteuser/<string:param>', methods=['DELETE'], view_func=deleteuser)

app.add_url_rule('/check-status/<string:id_user>', methods=['GET'], view_func=check_status_online)
app.add_url_rule('/users-online', methods=['GET'], view_func=get_list_user_online)


# User register
@app.route('/register', methods=["GET", "POST"])
def verifylink():
    try:
        json = request.json
        print(json)
        if bool(json):
            print(json["user_name"])
            user = Users.query.filter(or_(Users.user_name == json["user_name"], Users.gmail == json["gmail"])).first()
            if not user:
                token = s.dumps(json, salt=app.config["SECURITY_PASSWORD_SALT"])
                link = url_for('confirm', token=token, _external=True)
                response = client.emails.send(
                    From="admin@samnotes.online",  # Địa chỉ email gửi
                    To=json['gmail'],
                    Subject="Confirm",
                    TextBody="SAMNOTES thanks for using our service. Your confirmation link is: \n " + link
                )

                return {'status': 200, 'message': "Please check your email or spam"}
            else:
                return make_response(jsonify({'status': 400, 'message': 'Account or gmail already exists'}), 400)
        else:
            return make_response(jsonify({'status': 400, 'message': 'Request fail. Please try again'}), 400)
    except Exception as e:
        return make_response(jsonify({'status': 500, 'message': str(e)}), 500)


@app.route('/confirm/<token>')
def confirm(token):
    try:
        json = s.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=3600)
        user = Users.query.filter_by(gmail=json['gmail']).first()
        if (user):
            return "Your account was already"
        else:
            createUser(json)
    except:
        return "Your link was expired. Try again"

    return "Confirm successfully. Try to login"


# User fogot password

@app.route('/resetPasswork', methods=["GET", "POST"])
def forgotPasswork():
    json = request.json
    try:
        if (bool(json)):
            print(json['gmail'])
            user = Users.query.filter(Users.gmail == json['gmail']).first()
            if (user):
                token = s.dumps(user.gmail, salt=app.config["SECURITY_PASSWORD_SALT"])
                msg = Message('Passwork reset request', sender=app.config['MAIL_USERNAME'], recipients=[json['gmail']])
                link = url_for('confirmforgotPassword', token=token, _external=True)
                # random_number = random.randint(1000000, 9999999)
                # msg.body="To reset passwork, please click on this link    "+link
                # mail.send(msg)
                print(token)
                response = client.emails.send(
                    From="admin@samnotes.online",  # Địa chỉ email gửi
                    To=user.gmail,
                    Subject="Passwork resset request",
                    TextBody="To reset passwork, please click on this link    " + link
                )
                user.password_hash = (str(random_number))
                db.session.commit()
                # print("Error:", str(forgotPasswork))
                return {'status': 200, 'message': "Please check your email or spam"}
            else:
                return make_response(jsonify({'status': 400, 'message': 'Account or gmail no exists'}), 400)
        else:
            return make_response(jsonify({'status': 400, 'message': 'Request fail. Please try again'}), 500)

    except Exception as e:
        print(e)
        return make_response(jsonify({'status': 400, 'message': 'Request fail. Please try again'}), 400)


@app.route('/confirm_fogot/<token>')
def confirmforgotPassword(token):
    try:
        json = s.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600)
        fogot(json)

    except Exception as e:
        print(e)
        return "Your link was expired!!!!. Try again"
    return "Updated password succsess "


# User change password
@app.route('/login/change_password/<id>', methods=["GET", "POST"])
def changePassword(id):
    if (request.method == 'POST'):
        try:
            json = request.json
            user = Users.query.filter(Users.id == id).first()
            # old_passwork=json.get('password')
            # new_passwork=json.get("new_password")
            password_matched = pbkdf2_sha256.verify(json['password'], user.password_hash)
            token = s.dumps(json, salt=app.config["SECURITY_PASSWORD_SALT"])
            link = url_for('confirmgmail', token=token, _external=True)
            print(token)
            if (user.gmail == json["gmail"]):
                if (password_matched):
                    response = client.emails.send(
                        From="admin@samnotes.online",  # Địa chỉ email gửi
                        To=user.gmail,
                        Subject="Passwork change request",
                        TextBody="To change passwork, please click on this link: " + link
                    )
                    return {'status': 200, 'message': "Please check your email or spam"}
                else:
                    
                    return "password is not correct"
            else:
                return "Gmail is not correct"
        except Exception as e:
            print(e)
            return "password is not correct"


@app.route('/confirm_change/<token>')
def confirmgmail(token):
    try:
        json = s.loads(token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=2000)
        print(json)
        change(json)
        return "Updated password succsess "        
    # except Exception as e:
    #     print(e)
    #     return "Your link was expired!!!!."
    except Exception as e:  
            # Log the error message
        print("Error:", str(e))
        return {'status': 500, 'message': str(e)} 
