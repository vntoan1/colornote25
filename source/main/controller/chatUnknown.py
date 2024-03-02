from source import app

from source.main.function.handleChatUnknowns import *

app.add_url_rule('/chat-unknown/<string:param>',
                 methods=['GET', 'POST', "PATCH", "DELETE"], view_func=handleChatUnknowns)
app.add_url_rule('/message/chat-unknown/<string:id>',
                 methods=['GET','POST'], view_func=handleMessages)
app.add_url_rule('/message/unknown/<string:id>',
                         methods=['POST'], view_func=handleMessages)

