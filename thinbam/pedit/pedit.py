# Python EDIT
import sys
import pysam
import array
import numpy as np
from tags import _tagDefs
from pbcore.io import SubreadSet

def _openSubreadBam( bam_file ):
	try:
		bam_rdr = pysam.Samfile( bam_file, "r", check_sq = False )
		print 'Opening subreads.bam file succeeded...'
		return bam_rdr

	except IOError:
		print 'Failed to open subreads.bam file'
		sys.exit(1)

def _prepareOutputBam( output_bam_file, template_rdr ):
	try:
		bam_out = pysam.Samfile( output_bam_file, "wb", template = template_rdr )
		return bam_out

	except IOError:
		print 'Failed to prepare output.bam for writing'
		sys.exit(1)

def _validateInternalMode( bam_file ):
	print 'Determining whether movie was collected with internal mode...'
	bam_rdr = _openSubreadBam( bam_file )
	try: # check that dataset was run in internal mode by looking for start frame tag
		subread_iterator = bam_rdr.fetch( until_eof = True )
		first_subread = subread_iterator.next()
		first_subread.get_tag( 'pw' )
		print 'Validation of internal mode succeeded...'
		bam_rdr.close()

	except KeyError:
		print 'Validation of internal mode failed'
		sys.exit(1)

def _exciseRejectedBaseInfo ( subread, accept_ixs, reject_ixs ):
	by_base_tags = ['dq', 'dt', 'iq', 'mq', 'sq', 'st', 'ip', 'pw', 'pv']

	if reject_ixs:
		ipd = subread.get_tag( 'pd' ); ipd_type_code = ipd.typecode
		pw  = subread.get_tag( 'px' )

		# include ipd/pw from rejected pulses into next accepted basecall
		for index in reversed( accept_ixs ):
			reject = index - 1
			while reject in reject_ixs:
				try:
					ipd[ index ] += ipd[ reject ] + pw[ reject ]
					reject -= 1
				except OverflowError:
					ipd[ index ] = 65535
					reject -= 1

		ipd = np.array( ipd )
		accept_ipd = ipd[ accept_ixs ]

		# modify basecall features
		for tag in by_base_tags:
			if tag == 'ip':
				accept_ipd = array.array( ipd_type_code, accept_ipd )
				subread.set_tag( tag, accept_ipd )
			else:
				data = subread.get_tag( tag );
				if type( data[0] ) == str:
					accepted_data = [ data[i] for i in accept_ixs ]
					accepted_data = ''.join( accepted_data )
				else:
					data_type_code = data.typecode
					data = np.array( data )
					accepted_data = data[ accept_ixs ]
					accepted_data = array.array( data_type_code, accepted_data )
				subread.set_tag( tag, accepted_data )

	return subread

def _setSubreadTagsThinned( subread ):
	pw = subread.get_tag( 'px' )
	accept_indices = [ ix for ix,pulse_width in enumerate( pw ) if pulse_width > 1 ] 
	reject_indices = [ ix for ix,pulse_width in enumerate( pw ) if pulse_width <= 1 ]
	if reject_indices and (len( pw ) - len( reject_indices )) > 0:

		subread = _exciseRejectedBaseInfo( subread, accept_indices, reject_indices )
		pc = subread.get_tag( 'pc' ); pc_cp = '';
		for pulse_index,pulse_call in enumerate( pc ):
			if pulse_index in reject_indices:
				pc_cp += pulse_call.lower()
			else:
				pc_cp += pulse_call	

		subread.set_tag( 'pc', pc_cp )

		ixs = [ ix for ix,base in enumerate( pc_cp ) if not base.islower() ] # get indices of all pulsecalls that weren't lowercase (i.e. rejected as bases)
		subread.seq  = ''.join( [ subread.seq[i] for i in ixs ] )
		subread.qual = ''.join( [ '=' for i in ixs ] )
		query_name = subread.query_name.split( '_' )
		query_end = int( query_name[-1] )
		deficit = len( pc ) - len( subread.seq )
		query_end = query_end - deficit # correct end of query by number of rejected pulses
		subread.set_tag( 'qe', query_end )
		query_name[-1] = str( query_end )
		query_name = '_'.join( query_name )
		subread.query_name = query_name

	

	return subread

def _generateSubreadSet( output_bam_file ):
	sset = SubreadSet( output_bam_file, generateIndices = True )
	
	sset_output_name = output_bam_file[:-12] + 'subreadset.xml'
	sset.name = sset_output_name.split( '.' )[0]
	sset.write( sset_output_name )
	return sset_output_name

def thinBam( bam_file, output_bam_file ):
	_validateInternalMode( bam_file )
	bam_rdr = _openSubreadBam( bam_file )
	bam_out = _prepareOutputBam( output_bam_file, bam_rdr )

	print 'Thinning subreads.bam file...'
	for subread in bam_rdr.fetch( until_eof = True ):
		subread = _setSubreadTagsThinned( subread )
		bam_out.write( subread )

	bam_rdr.close()
	bam_out.close()

	print 'Indexing subreads.bam file and generating SubreadSet...'
	subreadSetXml = _generateSubreadSet( output_bam_file )
	return subreadSetXml
