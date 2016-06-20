from setuptools import setup, Extension, find_packages
import os.path
import sys

REQUIREMENTS_TXT = "requirements.txt"

if( "install" in sys.argv ) and sys.version_info < (2, 7, 0):
	print "thinbam requires Python 2.7 or greater"
	sys.exit(-1)

globals = {}
execfile( "thinbam/__version__.py", globals )
__VERSION__ = globals[ "__VERSION__" ]

def _get_local_file( file_name ):
	return os.path.join( os.path.dirname(__file__), file_name )

def _get_requirements( file_name ):
	with open( file_name, 'r' ) as f:
		reqs = [ line for line in f if not line.startswith( '#' ) ]
	return reqs

def _get_local_requirements( file_name ):
	return _get_requirements( _get_local_file(file_name) )

setup( 
	name = "thinbam",
	version = __VERSION__,
	author = "Kristofor Nyquist", 
	author_email = "knyquist@pacificbiosciences.com",
	description = "Remove single-frame pulsecalls from bam file",
	packages = find_packages( '.' ),
	zip_safe = True,
	entry_points = {
		"console_scripts" : [ "thinbam = thinbam.main:main" ]
	},
	install_requires = _get_local_requirements( REQUIREMENTS_TXT )
)