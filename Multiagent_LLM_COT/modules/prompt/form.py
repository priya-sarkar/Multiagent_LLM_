summarizer_output_form = ''' Extract agent's location after last round and present it in the ordered format 
'Position: Location'. 
Extract the position of bombs defused in this round and present it in the 
format 'Defused: Location’. '''

agent_output_form = '''Strictly follow the format ' Reasoning:..., Closest Bomb: Location , Position: Location, Defused: Location ' to answer. 
In the 'Reasoning:' section, describe your thought process. 
In the 'Closest Bomb:' section, provide the location of bomb that is nearest to you. 
In the 'Position:' section, provide the numeric position you wish to move to in this round, without any extra text. 
In the 'Defused:' if you defused a bomb in this round by going to bomb location,
report its numeric position here, without any extra text.'''

