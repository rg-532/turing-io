machine foo:
    @a:             # indent 4
  if 'a' goto exit  # indent 2
    # indent 4
  if 'b':
      do_stuff
  @b
      no_dedent
  dedent
