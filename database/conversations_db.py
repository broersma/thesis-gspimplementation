import MySQLdb as mdb

import re
def getConversations(get_variables = False, replace_others = False):

    conversations = []
    variables = []

    ################ get conversations
    con = None
    try:
        con = mdb.connect('localhost', 'db_user', 'db_pass', 'petshopgame_experiment1_derivative');
        cur = con.cursor()

        cur.execute("SELECT conversation_id FROM log GROUP BY conversation_id LIMIT 100;")

        conversation_ids = cur.fetchall()

        for conversation_id in conversation_ids:
            cur.execute("SELECT IF(utterance='enter_action' OR utterance = 'leave_action',-1,is_shopkeep) AS is_shopkeep, utterance \
                           FROM log WHERE conversation_id = %s;",
                           conversation_id[0])
            utterances = cur.fetchall()


            variables.append([])

            def getReplaceAndStoreVariableForRole(role):
                def replaceAndStoreVariable(matchobj):
                    variables[-1].append((role, matchobj.group(1), re.sub(r'<[^>]*>',r'',matchobj.group(2))))
                    return "#" + matchobj.group(1)
                return replaceAndStoreVariable

            if replace_others:
                utterances = [(u,re.sub(r'<(.+?)><other>(.+?)</other></\1>',r'#other_\1',str(s))) for (u,s) in list(utterances)]

            if get_variables:
                cleaned_utterances = [(u,re.sub(r'<[^>]*>',r'',re.sub(r"<(reason_to_say_yes|reason_to_say_no|type_of_animal|sum_of_money|pet_property)>(.+?)</\1>",getReplaceAndStoreVariableForRole(u),str(s)))) for (u,s) in list(utterances)]
            else:
                cleaned_utterances = [(u,re.sub(r'<[^>]*>',r'',str(s))) for (u,s) in list(utterances)]

            # add number of previous occurences within conversation to an utterance
            numbered_utterances = []
            for utterance in cleaned_utterances:
                i = 0
                utterance = (int(utterance[0]),) + utterance[1:]
                while utterance + (i,) in numbered_utterances:
                    i+=1
                numbered_utterances.append(utterance + (i,) )

            conversations.append(numbered_utterances)

    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if con:
            con.close()

    if get_variables:
        return conversations, variables
    else:
        return conversations
