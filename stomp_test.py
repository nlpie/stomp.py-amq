# test stomp -> amq
# see https://stackoverflow.com/questions/9328863/stomp-py-return-message-from-listener/10102673#10102673

# TODO: make class as sper: https://github.com/jasonrbriggs/stomp.py/issues/325

from stomp import *
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text
import time, ast

# db engine for read/write
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/notes')

# connection to AMQ via STOMP
c = Connection([('127.0.0.1', 61613)])

# custom listener class for receiving messages
class MyListener(ConnectionListener):
	def __init__(self):
		self.msg_list = []

	def on_error(self, frame):
		return self.msg_list.append('(ERROR) ' + frame.header + frame.body)

	def on_message(self, frame):
		return self.msg_list.append((frame.headers, frame.body))

# connect
c.connect('admin', 'admin', wait=True)

# instantiate
lst = MyListener()

# send dtest messages to AMQ
with engine.connect() as conn:
    #rs = conn.execute('SELECT * FROM notes order by random() limit 1000;')
    rs = conn.execute('SELECT * FROM notes;')
    for row in rs:
        #print(row.text)
        c.send('/queue/test', str({'text':row.text, 'id':row.note_id}), headers={"persistent":"true",
            "activemq.prefetchSize": 100})

# set listener
c.set_listener('', lst)

# subscribe client
#c.subscribe('/queue/test', id=1, ack='client-individual')
c.subscribe('/queue/test', id=1, ack='client')
#c.subscribe('/queue/test', id=1, ack='auto')

time.sleep(2)
messages = lst.msg_list

message_id = []

for m in messages:
    #print(m[0]['message-id'], ast.literal_eval(m[1])['text'],ast.literal_eval(m[1])['id'] )

    time.sleep(.5)
    # ack to acknowledge snarfing of message out of queue by message-id
    c.ack(m[0]['message-id'], 1)
    #messages.remove(m)
    message_id.append(m[0]['message-id'])
    print('len', len(message_id))

c.disconnect()


