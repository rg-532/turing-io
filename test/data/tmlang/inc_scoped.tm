

machine incrementer
	right until '_'

@loop:
	left
	if '1' do:
		write '0'
		goto loop

	write '1'
	left until '_'
	



