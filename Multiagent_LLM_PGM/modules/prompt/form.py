# agent_output_form = '''Strictly follow the 'Reasoning:..., Position: , Defused: ' format to provide your answer.
# In the 'Reasoning' section, describe your thought process.
# In the 'Position' section, only provide the numeric position you wish to move to in this round, without any extra text.
# In the 'Defused' section, only provide the numeric position of bomb defused by you in this round, without any extra text.
# '''

summarizer_output_form = ''' Extract agent's location after last round and present it in the ordered format 
'Position: Location'. 
Extract the position of bombs defused in this round and present it in the 
format 'Defused: Location’. '''

agent_output_form = '''Follow the format ' <Start of Response > Reasoning:...,Position: Location , Defused: Location <End of Response>' to answer.
In the 'Reasoning:' section, describe your thought process.
In the 'Position:' section, provide the numeric position you wish to move to in this round, without any extra text.
In the 'Defused:' if you defused a bomb in this round by going to bomb location, report its numeric position here, without any extra text.
'''