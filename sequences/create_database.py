import os, sys, inspect
module_folders = ["../database", "../gsp"]
for module_folder in module_folders:
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], module_folder)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
        
import conversations_db
import argparse

def get_database(index_per_line = False, num_conversations = None):
    conversations = conversations_db.getConversations(replace_others = True)

    database = []
    for conversation in conversations[:num_conversations]:
        i = 0
        turns = []
        for line in conversation:
            if not index_per_line:
                i += 1
            line = line[:2]
            if not len(turns) or turns[-1][1][0][0] != line[0]:
                if index_per_line:
                    i += 1
                turns.append((i, []))
            turns[-1][1].append(line)

        database_entry = []
        for turn in turns:
            database_entry.append((turn[0], frozenset(turn[1])))

        database.append(database_entry)

    return database
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate a database file from MySQL, needs the MySQLDB module installed")
    parser.add_argument("output", help="database output file")
    args = parser.parse_args()
    
    key = 'conversation_database'
    database = get_database(index_per_line = True, num_conversations = None)
    pickle.dump({key:database}, open(args.output, 'wb'))