@echo on
REM python get_conversation_sequences.py -s 14 -x 1 -n 0.0 database_cached.txt .\experiment\frequent_sequences_14_1.dat
REM python get_conversation_sequences.py -s 14 -x 3 -n 0.0 database_cached.txt .\experiment\frequent_sequences_14_3.dat
python get_conversation_sequences.py -s  3 -x 3 -n 0.0 database_cached.txt .\experiment\frequent_sequences_3_3.dat
python get_conversation_sequences.py -s  5 -x 5 -n 0.0 database_cached.txt .\experiment\frequent_sequences_5_5.dat
@echo on