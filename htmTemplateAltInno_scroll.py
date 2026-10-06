script_col_noscroll = '''
<div id = "altinno_col_noscroll"/>
'''

script_col_scroll = '''
<div id = "altinno_col_scroll"/>
'''

script_col_active = '''
<style>
[data-testid='column']:has(div#altinno_col_scroll):not(:has(div#altinno_col_noscroll))
{
overflow: auto;
height: 70vh;
display: flex;
flex-direction: column-reverse;}
</style>
'''
