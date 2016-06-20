# Python RESolve
import os
import xml.etree.ElementTree as ET

def getPrimaryFolder( jobID ):
	# this is ugly. learn to properly navigate xml tree and do tree search.
	rootdir  = jobID[0:3];
	linkjob  = jobID;
	filename = '/pbi/dept/secondary/siv/smrtlink/smrtlink-beta/jobs-root/' + rootdir + '/' + linkjob + '/tasks/pbcoretools.tasks.subreadset_align_scatter-1/chunk_subreadset_0.subreadset.xml'
	xml_tree = ET.parse( filename )
	root = xml_tree.getroot()
	for layer1 in root:
		if 'ExternalResources' in layer1.tag:
			for layer2 in layer1:
				if 'ExternalResource' in layer2.tag:
					for tup in layer2.items():
						if tup[0] == 'ResourceId':
							folder = tup[1].split('/')
							folder = folder[0:-1]
							folder = '/'.join( folder )
							return folder # found primary folder

	print 'Found xml pointer file, but was unable to find primary folder path'
	return None

def resolveBam( jobID ):
	primary_path = getPrimaryFolder( jobID )
	files = os.listdir( primary_path )
	subreads_file_name = [ f for f in files if f.find( 'subreads.bam' ) != -1 and f.find( 'control' ) == -1 and f[-3:] == 'bam' ]
	if len( subreads_file_name ) != 1:
		print 'there should only be one subreads.bam file'
		return None
	else:
		return primary_path + '/' + subreads_file_name[0]