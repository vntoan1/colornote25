import os.path
from datetime import datetime
from sqlalchemy import desc
import asyncio

from flask_cors import cross_origin

from source.main.model.datas import Datas
from source.main.model.nbnotes import Nbnotes
from source.main.model.notes import Notes

PATH_IMAGE = r"/home/thinkdiff/Documents/ImageNote"
from source import app

from flask import jsonify, make_response, request, url_for, send_from_directory, session
from passlib.hash import pbkdf2_sha256
from sqlalchemy import text

from source import db
from source.main.function.middleware import *
from source.main.model import *
from source.main.model.users import Users

import random

# from pyfcm import FCMNotification

import uuid


def getNotes(notes):
    data = []
    for note in notes:
        note_parse = {}
        if note.Notes.type == "checklist":
            flag = False
            if len(data) > 0:
                for item in data:
                    if (
                        item["type"] == "checklist"
                        and item["idNote"] == note.Notes.idNote
                    ):
                        flag = True
                        item["data"].append(
                            {
                                "content": note.Datas.content,
                                "status": note.Datas.doneContent,
                                "id": note.Datas.idData,
                            }
                        )
            if not flag:
                note_parse["idNote"] = note.Notes.idNote
                note_parse["type"] = note.Notes.type
                note_parse["data"] = [
                    {
                        "content": note.Datas.content,
                        "status": note.Datas.doneContent,
                        "id": note.Datas.idData,
                    }
                ]
                note_parse["title"] = note.Notes.title
                note_parse["doneNote"] = note.Notes.doneNote
                note_parse["createAt"] = str(note.Notes.createAt)
                note_parse["dueAt"] = (
                    str(note.Notes.dueAt) if note.Notes.dueAt else note.Notes.dueAt
                )
                note_parse["remindAt"] = (
                    str(note.Notes.remindAt)
                    if note.Notes.remindAt
                    else note.Notes.remindAt
                )
                note_parse["lock"] = note.Notes.lock
                note_parse["pinned"] = note.Notes.pinned
                note_parse["notePublic"] = note.Notes.notePublic
                note_parse["linkNoteShare"] = note.Notes.linkNoteShare
                note_parse["idUser"] = note.Notes.idUser
                note_parse["updateAt"] = note.Notes.updateAt
                note_parse["color"] = {
                    "r": note.Notes.r,
                    "g": note.Notes.g,
                    "b": note.Notes.b,
                    "a": note.Notes.a,
                }
        if note.Notes.type == "text" or note.Notes.type == "scan":
            note_parse["idNote"] = note.Notes.idNote
            note_parse["type"] = note.Notes.type
            note_parse["data"] = note.Datas.content
            note_parse["title"] = note.Notes.title
            note_parse["doneNote"] = note.Notes.doneNote
            note_parse["createAt"] = str(note.Notes.createAt)
            note_parse["dueAt"] = (
                str(note.Notes.dueAt) if note.Notes.dueAt else note.Notes.dueAt
            )
            note_parse["remindAt"] = (
                str(note.Notes.remindAt) if note.Notes.remindAt else note.Notes.remindAt
            )
            note_parse["lock"] = note.Notes.lock
            note_parse["pinned"] = note.Notes.pinned
            note_parse["idUser"] = note.Notes.idUser
            note_parse["notePublic"] = note.Notes.notePublic
            note_parse["linkNoteShare"] = note.Notes.linkNoteShare
            note_parse["updateAt"] = note.Notes.updateAt
            note_parse["color"] = {
                "r": note.Notes.r,
                "g": note.Notes.g,
                "b": note.Notes.b,
                "a": note.Notes.a,
            }
        if note.Notes.type == "image" or note.Notes.type == "screenshot":
            note_parse["idNote"] = note.Notes.idNote
            note_parse["type"] = note.Notes.type
            note_parse["data"] = note.Datas.content
            note_parse["title"] = note.Notes.title
            note_parse["doneNote"] = note.Notes.doneNote
            note_parse["createAt"] = str(note.Notes.createAt)
            note_parse["dueAt"] = (
                str(note.Notes.dueAt) if note.Notes.dueAt else note.Notes.dueAt
            )
            note_parse["remindAt"] = (
                str(note.Notes.remindAt) if note.Notes.remindAt else note.Notes.remindAt
            )
            note_parse["lock"] = None
            note_parse["metaData"] = note.Notes.metaData
            note_parse["notePublic"] = note.Notes.notePublic
            note_parse["linkNoteShare"] = note.Notes.linkNoteShare
            note_parse["pinned"] = note.Notes.pinned
            note_parse["idUser"] = note.Notes.idUser
            note_parse["updateAt"] = note.Notes.updateAt
            note_parse["color"] = {
                "r": note.Notes.r,
                "g": note.Notes.g,
                "b": note.Notes.b,
                "a": note.Notes.a,
            }
        if note_parse:
            data.append(note_parse)
    freshData = []
    for note_parse in data:
        if note_parse["lock"]:
            note_parse["lock"] = "*******"
            note_parse["data"] = "Locked"
        freshData.append(note_parse)
    return freshData


def specific_string(length):
    sample_string = "pqrstuvwxy"  # define the specific string
    # define the condition for random string
    result = "".join((random.choice(sample_string)) for x in range(length))
    print(" Randomly generated string is: ", result)


def getNote(param, lock=False, babel=False):
    notes = db.session.execute(
        text(
            "Select * from (select * from notes where notes.idNote={}) as b inner join datas on b.idNote=datas.idNote".format(
                param
            )
        )
    )
    note_parse = {}

    flag = False

    for note in notes:
        if note.type == "checklist":
            if flag == False:
                flag = True
                note_parse["idNote"] = note.idNote
                note_parse["type"] = note.type
                note_parse["data"] = []
                note_parse["title"] = note.title
                note_parse["doneNote"] = note.doneNote
                note_parse["createAt"] = str(note.createAt)
                note_parse["dueAt"] = str(note.dueAt) if (note.dueAt) else note.dueAt
                note_parse["remindAt"] = (
                    str(note.remindAt) if (note.remindAt) else note.remindAt
                )
                note_parse["lock"] = None
                note_parse["pinned"] = note.pinned
                note_parse["notePublic"] = note.notePublic  # ___SONPIPI____
                note_parse["linkNoteShare"] = note.linkNoteShare  # ___SONPIPI____
                note_parse["idUser"] = note.idUser
                note_parse["updateAt"] = note.updateAt
                note_parse["color"] = {
                    "r": note.r,
                    "g": note.g,
                    "b": note.b,
                    "a": note.a,
                }
            if flag == True:
                note_parse["data"].append(
                    {
                        "content": note.content,
                        "status": note.doneContent,
                        "id": note.idData,
                    }
                )

        if note.type == "text" or note.type == "scan":
            note_parse["idNote"] = note.idNote
            note_parse["type"] = note.type
            note_parse["data"] = note.content
            note_parse["title"] = note.title
            note_parse["doneNote"] = note.doneNote
            note_parse["createAt"] = str(note.createAt)
            note_parse["notePublic"] = note.notePublic  # ___SONPIPI____
            note_parse["linkNoteShare"] = note.linkNoteShare  # ___SONPIPI____
            note_parse["dueAt"] = str(note.dueAt) if (note.dueAt) else note.dueAt
            note_parse["remindAt"] = (
                str(note.remindAt) if (note.remindAt) else note.remindAt
            )
            note_parse["lock"] = None
            note_parse["pinned"] = note.pinned
            note_parse["idUser"] = note.idUser
            note_parse["updateAt"] = note.updateAt
            note_parse["color"] = {"r": note.r, "g": note.g, "b": note.b, "a": note.a}
        if note.type == "image" or note.type == "screenshot":
            note_parse["idNote"] = note.idNote
            note_parse["type"] = note.type
            note_parse["data"] = note.content
            note_parse["title"] = note.title
            note_parse["notePublic"] = note.notePublic  # ___SONPIPI____
            note_parse["linkNoteShare"] = note.linkNoteShare  # ___SONPIPI____
            note_parse["doneNote"] = note.doneNote
            note_parse["createAt"] = str(note.createAt)
            note_parse["dueAt"] = str(note.dueAt) if (note.dueAt) else note.dueAt
            note_parse["remindAt"] = (
                str(note.remindAt) if (note.remindAt) else note.remindAt
            )
            note_parse["lock"] = None
            note_parse["metaData"] = note.metaData
            note_parse["pinned"] = note.pinned
            note_parse["idUser"] = note.idUser
            note_parse["updateAt"] = note.updateAt
            note_parse["color"] = {"r": note.r, "g": note.g, "b": note.b, "a": note.a}

    if note.lock:
        if lock == True or babel == True:
            note_parse["data"] = "Locked"
        note_parse["lock"] = "*******"
    return note_parse


def getOnlyNote(idNote):
    if request.method == "GET":
        try:
            note = Notes.query.filter(Notes.idNote == idNote).first()
            if note:
                note.view = int(note.view) + 1
                db.session.commit()
                return {"note": getNote(idNote, babel=True)}
            else:
                return "Note does not exist"  # Return an appropriate message when the note is not found
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )

        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


def genLinkWebNotes(idNote):
    if request.method == "GET":
        return {"note": getNote(idNote, babel=True)}


def changePrivateNotes(idNote):
    if request.method == "PATCH":
        try:
            note = Notes.query.filter(Notes.idNote == idNote).first()
            data = request.json

            private = data.get("notePublic", "0")
            note.notePublic = private
            db.session.add(note)
            db.session.commit()
            return jsonify({"status": 200, "message": "Note is private"})
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


def getPublicNotes():
    try:
        notes = (
            db.session.query(Notes, Datas, Users)
            .join(Users, Users.id == Notes.idUser)
            .join(Datas, Datas.idNote == Notes.idNote)
            .filter(Notes.notePublic == 1 and Notes.inArchived == 1)
            .order_by(desc(Notes.updateAt))
            .limit(10)
        )

        list_public_notes = []
        for note in notes:
            public_note = {
                "title": note.Notes.title,
                "type": note.Notes.type,
                "content": note.Datas.content,
                "update_at": note.Notes.createAt,
                "author": note.Users.user_name,
            }
            list_public_notes.append(public_note)

        return (
            jsonify(
                {"status": 200, "message": "success", "public_note": list_public_notes}
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": 500, "message": f"Something went wrong!", "error": str(e)}
            ),
            500,
        )
    # if (request.method == "GET"):
    #     notes = db.session.execute(text(
    #         'Select * from (select * from notes where notes.notePublic=1 and notes.inArchived=1) as b inner join datas on b.idNote=datas.idNote'))
    #     return {"notes": getNotes(notes)}


def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


@cross_origin()
def handleNotes(param):

    try:
        if request.method == "GET":

            notes = (
                db.session.query(Notes, Datas)
                .join(Datas, Datas.idNote == Notes.idNote)
                .filter(Notes.inArchived == 1 and Notes.idUser == param)
                .order_by(desc(Notes.updateAt))
                .all()
            )

            return {"notes": getNotes(notes)}

        if request.method == "POST":
            print("SONPRO_PHAN_POST___handleNotes___" + str(request.json))
            try:
                json = request.json
                nbnote = Nbnotes.query.filter(Nbnotes.idUser == param).first()
                note_lock = False
                print(json)
                color = json["color"]
                date_dueAt = None
                if json["dueAt"]:
                    date_dueAt = datetime.strptime(
                        json["dueAt"], "%d/%m/%Y %I:%M %p %z"
                    )
                date_rmAt = None
                if json["remindAt"]:
                    date_rmAt = datetime.strptime(
                        json["remindAt"], "%d/%m/%Y %I:%M %p %z"
                    )
                lockPass = None

                if json["lock"]:
                    lockPass = pbkdf2_sha256.hash(json["lock"])

                if lockPass:
                    note_lock = True
                #   linkNoteShare
                note = {}
                if "metaData" in json:
                    if "notePublic" in json:
                        linkNoteShare = my_random_string(6)
                        note = Notes(
                            idUser=param,
                            idFolder=json["idFolder"],
                            type=json["type"],
                            title=json["title"],
                            pinned=json["pinned"],
                            dueAt=date_dueAt,
                            remindAt=date_rmAt,
                            lock=lockPass,
                            r=color["r"],
                            g=color["g"],
                            b=color["b"],
                            a=color["a"],
                            metaData=json["metaData"],
                            linkNoteShare=json["linkNoteShare"],
                            notePublic=json["notePublic"],
                        )
                    else:
                        note = Notes(
                            idUser=param,
                            idFolder=json["idFolder"],
                            type=json["type"],
                            title=json["title"],
                            pinned=json["pinned"],
                            dueAt=date_dueAt,
                            remindAt=date_rmAt,
                            lock=lockPass,
                            r=color["r"],
                            g=color["g"],
                            b=color["b"],
                            a=color["a"],
                            metaData=json["metaData"],
                            linkNoteShare=json["linkNoteShare"],
                            notePublic=0,
                        )
                else:
                    if "notePublic" in json:
                        linkNoteShare = my_random_string(6)
                        note = Notes(
                            idUser=param,
                            idFolder=json["idFolder"],
                            type=json["type"],
                            title=json["title"],
                            pinned=json["pinned"],
                            dueAt=date_dueAt,
                            remindAt=date_rmAt,
                            lock=lockPass,
                            r=color["r"],
                            g=color["g"],
                            b=color["b"],
                            a=color["a"],
                            notePublic=json["notePublic"],
                            linkNoteShare=json["linkNoteShare"],
                        )
                    else:
                        note = Notes(
                            idUser=param,
                            idFolder=json["idFolder"],
                            type=json["type"],
                            title=json["title"],
                            pinned=json["pinned"],
                            dueAt=date_dueAt,
                            remindAt=date_rmAt,
                            lock=lockPass,
                            r=color["r"],
                            g=color["g"],
                            b=color["b"],
                            a=color["a"],
                            linkNoteShare=json["linkNoteShare"],
                            notePublic=0,
                        )
                print("SONPIPI_POST_NOTES_", str(note))
                db.session.add(note)
                if nbnote:
                    if note.notePublic == 1:
                        nbnote.nbnotes = int(nbnote.nbnotes) + 1
                else:
                    if note.notePublic == 1:
                        nbnote = Nbnotes(
                            idUser=param, nbnotes=1
                        )  # Create a new Nbnotes record if it doesn't exist
                        db.session.add(nbnote)
                # print("1")
                # if nbnote.nbnotes:
                #     nbnote.nbnotes = (int(nbnote.nbnotes) + 1)
                db.session.commit()
                if json["type"] == "checklist":
                    for each in json["data"]:
                        data = Datas(
                            idNote=note.idNote,
                            content=each["content"],
                            doneContent=each["status"],
                        )
                        db.session.add(data)
                else:
                    data = Datas(idNote=note.idNote, content=json["data"])
                    db.session.add(data)
                db.session.commit()
                return {
                    "status": 200,
                    "message": "Note was created successfully",
                    "note": getNote(note.idNote, note_lock),
                }
            except Exception as e:
                print(e)
                return make_response(
                    jsonify(
                        {"status": 400, "message": "Request fail. Please try again"}
                    ),
                    400,
                )
        if request.method == "PATCH":
            try:
                json = request.json

                note_query = Notes.query.get(param)

                for key in list(json.keys()):
                    if key == "dueAt":
                        date_dueAt = None
                        if json["dueAt"]:
                            date_dueAt = datetime.strptime(
                                json["dueAt"], "%d/%m/%Y %I:%M %p %z"
                            )
                            formatted_dueAt = date_dueAt.strftime(
                                "%Y-%m-%d %I:%M %p %z"
                            )
                        note_query.dueAt = date_dueAt
                        # note_query.dueAt = str(formatted_dueAt)
                        print(str(formatted_dueAt))
                        print(date_dueAt)
                    if key == "notePublic":
                        notePublic = json["notePublic"]
                        note_query.notePublic = notePublic
                        linkNoteShare = my_random_string(6)
                        note_query.linkNoteShare = linkNoteShare
                    if key == "remindAt":
                        date_rmAt = None
                        if json["remindAt"]:
                            date_rmAt = datetime.strptime(
                                json["remindAt"], "%d/%m/%Y %I:%M %p %z"
                            )
                        note_query.remindAt = date_rmAt
                    if key == "color":
                        color = json["color"]
                        note_query.r = color["r"]
                        note_query.g = color["g"]
                        note_query.b = color["b"]
                        note_query.a = color["a"]
                    if key == "title":
                        note_query.title = json["title"]
                    if key == "data":

                        if json["type"] == "text":
                            note_data = Datas.query.filter(
                                Datas.idNote == param
                            ).first()

                            note_data.content = json["data"]
                            db.session.add(note_data)

                        if json["type"] == "checklist":
                            trunc_data = Datas.query.filter(Datas.idNote == param).all()
                            for item in trunc_data:
                                db.session.delete(item)
                            db.session.commit()
                            for edit in json["data"]:
                                data = Datas(
                                    idNote=param,
                                    content=edit["content"],
                                    doneContent=edit["status"],
                                )
                                db.session.add(data)

                    if key == "pinned":
                        note_query.pinned = json["pinned"]
                    if key == "lock":
                        lockPass = None

                        if json["lock"]:
                            lockPass = pbkdf2_sha256.hash(json["lock"])
                        note_query.lock = lockPass
                note_query.updateAt = datetime.now()
                db.session.add(note_query)
                db.session.commit()
                return {
                    "status": 200,
                    "message": "Note was updated successfully",
                    "note": getNote(note_query.idNote, False),
                }
            except Exception as e:
                print(e)
                return make_response(
                    jsonify(
                        {"status": 400, "message": "Request fail. Please try again"}
                    ),
                    400,
                )
        if request.method == "DELETE":
            try:

                note_query = db.session.query(Notes).filter_by(idNote=param).first()
                note_query.inArchived = False
                note_lock = False
                if note_query.lock:
                    note_lock = True
                db.session.add(note_query)
                db.session.commit()
                return {
                    "status": 200,
                    "message": "Note was deleted successfully",
                    "note": getNote(note_query.idNote, note_lock),
                }
            except:
                return make_response(
                    jsonify(
                        {"status": 400, "message": "Request fail. Please try again"}
                    ),
                    400,
                )
    except Exception as e:
        return (
            jsonify(
                {"status": 500, "message": "Something went wrong!", "error": str(e)}
            ),
            500,
        )


def tickerBox(idData):
    if request.method == "PATCH":
        try:
            data = Datas.query.filter(Datas.idData == idData).first()
            data.doneContent = not data.doneContent
            db.session.add(data)
            db.session.commit()
            return {"status": 200, "message": "Note was update successfully"}
        except:
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


def delTruncNote(id):
    if request.method == "DELETE":
        try:
            note_query = db.session.query(Notes).filter_by(idNote=id).first()
            print(note_query)
            db.session.delete(note_query)
            db.session.commit()
            return {
                "status": 200,
                "message": "Note was deleted successfully",
            }
        except:
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


@cross_origin()
def trashGet(idUser):
    if request.method == "GET":
        notes = db.session.execute(
            text(
                "Select * from (select * from notes where notes.idUser={} and notes.inArchived=0) as b inner join datas on b.idNote=datas.idNote".format(
                    idUser
                )
            )
        )

        return {"notes": getNotes(notes)}


def trashRestore(id):
    if request.method == "POST":
        try:
            note_query = db.session.query(Notes).filter_by(idNote=id).first()
            note_query.inArchived = True
            db.session.add(note_query)
            db.session.commit()
            return {
                "status": 200,
                "message": "Note was restore successfully",
                "note": getNote(note_query.idNote),
            }
        except:
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


def getLastNote():
    try:
        if request.method == "GET":

            sql = db.session.execute(text("select max(idNote) as MaxId  from notes"))
            for note in sql:
                return {"status": 200, "idNoteLast": note.MaxId}
    except:
        return make_response(
            jsonify({"status": 400, "message": "Request fail. Please try again"}), 400
        )


def openLock(idNote):
    try:
        if request.method == "POST":
            json = request.json
            Note = Notes.query.filter(Notes.idNote == idNote).first()
            if pbkdf2_sha256.verify(json["pass_lock"], Note.lock):
                return {
                    "status": 200,
                    "note": getNote(idNote, False),
                    "pass_lock": json["pass_lock"],
                }
            else:
                return make_response(
                    jsonify({"status": 400, "message": "Password not true"}), 400
                )

    except:
        return make_response(
            jsonify({"status": 400, "message": "Request fail. Please try again"}), 400
        )


def getNotesShare(nid):
    if request.method == "GET":
        # note = Notes.query.filter(
        #         Notes.idNote == nid).first()
        return {"status": 200, "message": "Note get successfully", "note": getNote(nid)}


def searchNote():
    if request.method == "GET":
        try:
            notes = db.session.execute(
                text(
                    "Select * from (select * from notes where notes.notePublic=1 and notes.inArchived=1) as b inner join datas on b.idNote=datas.idNote"
                )
            )
            search_query = request.args.get("key", "")
            notes_data = []
            for row in notes:
                search = {}
                search["idNote"] = row.idNote
                search["title"] = row.title
                search["content"] = row.content
                search["type"] = row.type
                if search_query and row.title and row.content:
                    if (
                        search_query.lower() in row.title.lower()
                        or search_query.lower() in row.content.lower()
                    ):
                        notes_data.append(search)
            return {"status": 200, "search_note": notes_data}
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


# def subscription():
#     """
#         POST creates a subscription
#         GET returns vapid public key which clients uses to send around push notification
#     """

#     if request.method == "GET":
#         return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
#             headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")

#     subscription_token = request.get_json("subscription_token")
#     return Response(status=201, mimetype="application/json")
# def push_v1():
#     message = "Push Test v1"
#     print("is_json",request.is_json)

#     if not request.json or not request.json.get('sub_token'):
#         return jsonify({'failed':1})

#     print("request.json",request.json)

#     token = request.json.get('sub_token')
#     try:
#         token = json.loads(token)
#         send_web_push(token, message)
#         return jsonify({'success':1})
#     except Exception as e:
#         print("error",e)
#         return jsonify({'failed':str(e)})


def numberNotes():
    if request.method == "GET":
        try:
            notes = db.session.execute(
                text(
                    "Select * from users inner join nbnotes on users.id= nbnotes.idUser ORDER BY nbnotes.nbnotes DESC "
                )
            )
            index = 0
            data = []
            for user in notes:
                if index > 10:
                    break
                index += 1
                nbnote = {}
                nbnote["id"] = user.id
                nbnote["idUser"] = user.idUser
                nbnote["name"] = user.name
                nbnote["nbnote"] = user.nbnotes
                nbnote["Avatar"] = user.linkAvatar

                data.append(nbnote)
            return {"status": 200, "data": data}
        except Exception as e:
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


def getview():
    if request.method == "GET":  # Use parentheses for the condition
        try:
            notes = db.session.execute(text("Select * from notes"))
            data = []
            for row in notes:
                view_note = {}
                view_note["idNote"] = row.idNote
                view_note["idUser"] = row.idUser
                view_note["view"] = row.view
                data.append(view_note)
            return {"state": 200, "data": data}
        except Exception as e:
            print(e)
            return make_response(
                jsonify({"status": 400, "message": "Request fail. Please try again"}),
                400,
            )


def share_link():
    if request.method == "POST":
        json = request.json

        if "url" not in json:
            return jsonify({"error": "URL is missing in the request"}), 400

        shared_url = json["url"]
        message = f"Shared the link: {shared_url}"

        return jsonify({"message": message})
        # with app.test_request_context():
        #     profile_url = url_for('profile', username='john')
        #     print(f'Dường dẫn URL cho profile: {profile_url}')
        #     return {'state': 200, 'data': profile_url}


async def create_new_note_image(id_user):

    try:

        data = request.form
        image_note = request.files.get("image_note")
        noteCreate = (
            db.session.query(Notes, Datas, Users)
            .join(Datas, Datas.idNote == Notes.idNote)
            .join(Users, Users.id == Notes.idUser)
            .first()
        )
        print("___SONPRO___Tao_notes___" + str(data))
        if noteCreate is None:
            return jsonify({"status": 404, "message": "User not found"}), 404

        if not noteCreate.Users.statesLogin:
            return jsonify({"status": 401, "message": "User is not login"}), 401

        # remind = ''
        # if data['remind']:
        #     remind = data['remind']
        new_note = Notes(
            idUser=id_user,
            type=data["type"],
            title=data["title"],
            dueAt=datetime.now(),
            createAt=datetime.now(),
            r=data["r"],
            g=data["g"],
            b=data["b"],
            a=data["a"],
            linkNoteShare="Devil May Cry",
            notePublic=True,
            remindAt=data["remind"] if "remind" in data and data["remind"] else None,
        )
        print("create_new_note_image___Post_ANh___", new_note)
        db.session.add(new_note)
        db.session.commit()

        new_note.linkNoteShare = make_link_share(new_note.idNote)
        db.session.commit()

        new_data = Datas(
            idNote=new_note.idNote,
            content=data["content"],
            image=make_url_image(id_user, PATH_IMAGE, image_note, "note"),
        )
        db.session.add(new_data)
        db.session.commit()
        print("___SONPRO___NewNotes____" + str(PATH_IMAGE))
        new_note = {
            "id_note": new_note.idNote,
            "type": data["type"],
            "title": data["title"],
            "content": data["content"],
            "image_note": noteCreate.Datas.image,
        }
        return jsonify({"status": 200, "message": "Success", "Info": new_note}), 200
    except Exception as e:
        print("____Error from server:______ " + str(e))
        return make_response(jsonify("____Error from server:______ ", str(e)), 500)


def view_image(id_user, file_name):
    try:
        user_path = os.path.join(PATH_IMAGE, str(id_user))
        return send_from_directory(user_path, file_name)
    except Exception as e:
        return make_response(jsonify("Something went wrong: ", str(e)), 500)


def share_link_note(id_note):
    try:
        note = (
            db.session.query(Notes, Datas)
            .join(Datas, Datas.idNote == Notes.idNote)
            .filter(Notes.idNote == id_note)
            .first()
        )

        if note is None:
            return jsonify({"status": 404, "message": "Note is not valid!"}), 404
        if not note.Notes.notePublic:
            return jsonify({"status": 401, "message": "Note is not public"}), 401
        public_note = {
            "id_note": note.Notes.idNote,
            "id_folder": note.Notes.idFolder,
            "id_user": note.Notes.idUser,
            "id_group": note.Notes.idGroup,
            "type": note.Notes.type,
            "title": note.Notes.title,
            "color": {
                "r": note.Notes.r,
                "g": note.Notes.g,
                "b": note.Notes.b,
                "a": note.Notes.a,
            },
            "create_at": note.Notes.createAt,
            "content": note.Datas.content,
            "image": note.Datas.image,
            "link_note_share": note.Notes.linkNoteShare,
        }
        return jsonify({"status": 200, "message": "Success", "Note": public_note})
    except Exception as e:
        return jsonify({"status": 500, "message": f"Something went wrong! {e}"}), 500
