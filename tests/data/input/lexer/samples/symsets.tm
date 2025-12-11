machine symbol_sets:
	if ('a','b','c',) do:
		write 'x'
	elif ('d', 'e', 'f') do:
		write 'y'
	elif ('sym_1',
		  sym_iden_2,
		  call
	) do:
		write 'z'
	halt