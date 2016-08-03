import os

def mkdirp( path ):
	try:
		os.makedirs( path )
	except OSError:
		print 'Error in making directory, it most likely already exists. Will proceed under that assumption'
		# this should be verified
		pass
