# Wordpress to Rst convertor

Converts Wordpress blog posts in wordpress xml format to Restructured Text.

## Help:
Run on commandline. Use -h option to view command line options  

	-h, --help            show this help message and exit  
	-f FILE, --file=FILE  Wordpress export xml file  
	-o OUTFILE, --outfile=OUTFILE Filename to save output to (JSON)  
	-c, --convert         perform conversion to RestructedText  
	-s, --split-output    Split data into separate files eg -categories.json, -tags.json, -posts.json  
	-d, --dry-run         Performs a dry run, will not save any output  


## Examples:

The following example will convert a wordpress xml file to json and save it in json format in a file called myblog.json

	python parse.py -f myblog.xml -o myblog.json
	
This will convert to json and save split out the categories, tags and posts into separate files.

	python parse.py -f myblog.xml -o myblog.json -s
	
The following will split and convert to json with any html fields converted to Rst format.

	python parse.py -f myblog.xml -o myblog.json -c	-s
	
## Requirements:

The Rst conversion is done via <a href="http://johnmacfarlane.net/pandoc/">pandoc</a>, so this will need to be installed if conversion to Rst is required.