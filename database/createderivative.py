#!/usr/bin/python
# -*- coding: utf-8 -*-

# Creates derivative tables of the experimental data. Should be run only once. (But won't hurt if run multiple times.)

import MySQLdb as mdb
import sys
import re

conr = None
conw = None

# TODO
# SELECT COUNT(rowid), utterance FROM log GROUP BY utterance ORDER BY COUNT(rowid)
# SELECT COUNT(rowid), utterance FROM log WHERE utterance NOT LIKE '%<other>%' GROUP BY utterance ORDER BY COUNT(rowid)
# SELECT COUNT(rowid), utterance FROM log WHERE utterance LIKE '%<other>%' GROUP BY utterance ORDER BY COUNT(rowid)
# blank out any variable that has an OTHER_OPTION -> to find more equals

try:
        
    # connect to writable DB
    conw = mdb.connect('localhost', 'db_user', 'db_pass', 'petshopgame_experiment1_derivative');
    curw = conw.cursor()
    
    # create derivative log table (has 'utterance' instead of 'line')
    curw.execute("DROP TABLE log")
    curw.execute("CREATE TABLE log (rowid INT(11) PRIMARY KEY AUTO_INCREMENT, line_id INT, conversation_id INT, \
                                    user_id INT, is_event INT DEFAULT 0, timestamp TEXT, is_shopkeep INT, utterance TEXT)")
                      
    # prepare insert statement
    insertStmt = "INSERT INTO log (line_id, conversation_id, user_id, is_event, timestamp, is_shopkeep, utterance) \
                           VALUES (     %s,              %s,      %s,       %s,        %s,   %s,        %s)"

    # connect to readable DB
    conr = mdb.connect('localhost', 'db_user', 'db_pass', 'petshopgame_experiment1');
    curr = conr.cursor()
        
    # select lines from finished conversations only
    curr.execute("SELECT log.rowid, conversation_id, user_id, is_event, timestamp, \
                         (user_id = shopkeep_id) AS is_shopkeep, \
                         line \
                     FROM log \
                     JOIN conversation ON conversation.rowid = conversation_id \
                    WHERE conversation_id IN (SELECT conversation_id FROM log WHERE line = 'The customer leaves the store.|You leave the store.')")
                
    rows = curr.fetchall()
    
    for row in rows:
        rowid, conversation_id, user_id, is_event, timestamp, is_shopkeep, line = row
        
        # if utterance  
        if not is_event:
            for utterance in re.findall('<utterance>(.*?)</utterance>',line):
                newrow = row[:6] + (utterance, )
                curw.execute(insertStmt, newrow)
        # if action
        else:
            action = 'unknown_action'
            if line == 'A customer enters the pet shop.|You enter the pet shop.':
                action = 'enter_action'
            elif line == 'The customer leaves the store.|You leave the store.':
                action = 'leave_action'
            elif line == 'You give the animal to the customer.|The shopkeep gives the animal to you.':
                action = 'give_action'
            elif line == 'The customer pays for the animal.|You pay the shopkeep for the animal.':
                action = 'pay_action'
                
            newrow = row[:6] + (action,)
            curw.execute(insertStmt, newrow)

except mdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if conr:    
        conr.close()
