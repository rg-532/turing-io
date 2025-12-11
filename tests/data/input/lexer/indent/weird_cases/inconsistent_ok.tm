machine inconsistent:
  if 'b':       # +2 indent
      do 'a'    # +4 indent
      do 'b'
return_to_0     # -6 indent
    back_at_it  # +4 indent
         do 'c' # +4 indent
    return_to_4 # -4 indent
return_to_0     # -4 indent
 blaa           # +1 indent
  bleu          # +1 indent
   blee         # +1 indent
bye             # -3 indent