#!/usr/bin/env python
'''
Nagios Host ConFig (NHCF)

User specify a csv file and a template file.
The NHCF then parse the file and generate individual host configuration files into a folder.
The config files can then be used to import to Nagios Enterprise DB.


'''
import jinja2
import argparse
import os
import sys
import re
import csv

"""
_DIR=os.getcwd()+"/hosts/"
_CSV=os.getcwd()+"/multimedia_hosts.csv"
_TMPL="host_tmpl.cfg.j2"
_DELIMITER=""
"""
message_1="[i] No delimiter specify. The script has detected the delimiter:"
message_2="[i] Please specific the correct delimiter with the flag -f \";\"."
message_3="[i] Export completed successfully."
message_4="[e] Error in main:"
message_5="[?] Is this correct?"


class Host:pass

class NHCF:

    '''Read csv file, and parse them as '''
    def __init__( self ):
        self._filename = str()
        self._host_dict = {}

    def readfile( self, filename, delimiter ):
        with open( filename ) as f:
            header_line = f.readline()
            if delimiter == "":
                result = self.delimiter_analyser(header_line)
                print "%s %s"%(message_1,result)
                answer = raw_input("%s"%message_5)
                if answer == "\n" or answer == "n" or answer == "no" or answer == "No" or answer == "N":
                    print "%s"%(message_2)
                    sys.exit()
                delimiter = result
                
            header = header_line.strip().split( delimiter )

            for line in f:
                if line != "\n":
                    host = Host()
                    '''set up new Host attribute'''
                    for enum, attr in enumerate( header ) :
                        attr_with_enum = "%s_%s"%(attr, enum)
                        setattr( host, attr_with_enum, str() )

                    '''Pair data up based on index'''
                    host_entry = line.strip().split( delimiter )
                    for host_attr in sorted( host.__dict__, key=lambda x: int( x[ x.rfind('_')+1 : ] )):
                        index = host_attr.rfind('_')+1
                        host_data = host_entry[ int( host_attr[index:] )]
                        new_host_attr = host_attr[:index-1]
                        '''Can I modify host_attr and remove index from here'''
                        host.__dict__[ new_host_attr ] = host.__dict__.pop( host_attr )
                        setattr( host, "%s"%new_host_attr, host_data )
                        self._host_dict[ "%s"%host_entry[0] ] = host

    def exportfile( self, directory, hostname, result ):
        '''
        If directory doesn't exist, create it.
        '''
	if not os.path.exists( directory ):
	    os.mkdir(directory)
        """ Assume template name is xxx.yyy.cfg.j2"""
        with open( directory+"/"+hostname+".cfg",'w' ) as f:
            f.writelines(result)

    def delimiter_analyser( self, sample_line ):
        '''
        Take a few line as a sample and use pattern matching to analyse what delimiter it should be using.
        '''
        sniffer = csv.Sniffer()
        result = sniffer.sniff(sample_line)
        return result.delimiter 
        

def main():
    '''Process options'''
    parser = argparse.ArgumentParser(description='[i] Process CSV and convert each entry into Nagios hosts/hostgroups file.')
    parser.add_argument('-c', "--csv", help='[i] Specify CSV file to be used.')
    parser.add_argument('-t', "--template", help='[i] Specify which template to be used.')
    parser.add_argument('-d', "--directory", default="hosts", help='[i] Specify output directory for generated files.')
    parser.add_argument('-f', "--delimiter", default="", help='[i] Specify delimiter to be used.')
    args = parser.parse_args()
    nhcf = NHCF()
    if args.csv and args.template:
        nhcf.readfile( args.csv, args.delimiter )
        '''nhcf.readfile("nagios.csv")'''
    else:
        print "[?] Not enough arguments\n",args
        sys.exit()

    for hostname in nhcf._host_dict.keys():
        jinja_host=nhcf._host_dict[hostname].__dict__
        try:
            result=jinja2.Environment( loader = jinja2.FileSystemLoader('./')).get_template( args.template ).render(host=jinja_host)
            nhcf.exportfile( args.directory , hostname, result )
        except OSError as e:
            print "%s %s %s",message_4,__file__,e
    print "%s"%(message_3)

if __name__ == '__main__':
    main()
