
machine incrementer
	right until '_'

@loop:
	left
	if not '1' goto loop_exit
	write '0'
	goto loop

@loop_exit:
	write '1'
	left until '_'

