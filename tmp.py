if seq_size > 0:
    if self.pathBool.value() is False:
        constr = seq_niceName
    else:
        constr = sequence
else:
    seq_errors += 1
print "* " + constr + " .... " + sconvert(seq_size)