# test stomp -> amq
# see https://stackoverflow.com/questions/9328863/stomp-py-return-message-from-listener/10102673#10102673

from stomp import *
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text
import time

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
    rs = conn.execute('SELECT * FROM notes')
    for row in rs:
        #print(row.text)
    	c.send('/queue/test', str({'text':row.text, 'id':row.note_id}), persistent="true")

# set listener
c.set_listener('', lst)

# ssubscribe client
c.subscribe('/queue/test', id=1, ack='client')
time.sleep(2)
messages = lst.msg_list

print(messages)

# ack to snarf message out of queue by message-id
c.ack('mybroker-14aa2', 1)
c.disconnect()




