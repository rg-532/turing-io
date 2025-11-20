machine repl_a_b:

@loop_start:
right
if '' goto exit
if not 'a' goto loop_start
write 'b'
goto loop_start

@exit:
left until ''