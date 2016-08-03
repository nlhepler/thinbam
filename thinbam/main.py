import argparse, sys, os, os.path as op

from thinbam.utils import mkdirp
from thinbam.pres import resolveBam
from thinbam.pedit import thinBam
from pbcore.io import BamIO


def doValidate( args ):
	if args.SMRTLinkJobID:
		print 'Trying to resolve subreads.bam from SMRTLink Job ID...'
		try: # to get subreads.bam from SMRTLinkID
			bam_file = resolveBam( args.SMRTLinkJobID )
			print '   Found subreads.bam: ' + bam_file

		except IOError:
			print 'Could not resolve subreads.bam from SMRTLink Job ID'
			sys.exit(1)

	elif args.bamPath:
		bam_file = args.bamPath

	try: # validate subreads.bam by opening it with pbcore
		BamIO.BamReader( bam_file )
		print 'Validation of subreads.bam file succeeded...'
		return bam_file

	except IOError:
		print 'Could not validate subreads.bam by opening with pbcore.'
		sys.exit(1)

def doThinning( args ):
	bam_file = doValidate( args )
	thinBam( bam_file, args.outputBam )

def parseArgs():
	parser = argparse.ArgumentParser( prog = "thinbam" )
	parser.add_argument(
		"--SMRTLinkJobID", "-j",
		action = "store", type = str )
	parser.add_argument(
		"--bamPath", "-p",
		action = "store", type = str )
	parser.add_argument(
		"--outputBam", "-o",
		default = "out",
		action = "store",  type = str )
	parser.add_argument(
		"--pdb", action = "store_true",
		help = "Drop into debugger on exception" )

	subparsers = parser.add_subparsers( help = "sub-command help", dest = "command" )
	validate = subparsers.add_parser( "validate", help = "Validate the subreads.bam" )
	segment = subparsers.add_parser( "thin", help = "Peform thinning of subreads.bam" )

	args = parser.parse_args()
	return args

def _makeOutputDirectory( args ):
	output = args.outputBam
	output = output.split( '/' )
	output_bam = output[-1]
	output_dir = output[0:-1]
	output_dir = '/'.join( output_dir )
	try:
		mkdirp( output_dir )
	except:
		print 'Failed to create output directory'
		sys.exit(1)

def _main( args ):
	print '**this is the experimental version**'

	if args.command == "validate":
		doValidate( args )
		return

	elif args.command == "thin":
		_makeOutputDirectory( args )
		doThinning( args )

	print 'Done.' 

def main():
	args = parseArgs()
	if args.pdb:
		try:
			import ipdb
			with ipdb.launch_ipdb_on_exception():
				_main( args )
			return

		except ImportError:
			_main( args )
	else:
		_main( args )


if __name__ == '__main__':
	main()