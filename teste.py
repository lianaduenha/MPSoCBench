import json, argparse, sys, includes
from configparser     import ConfigParser


def command_line_handler():
	parser = argparse.ArgumentParser()

	parser.add_argument('configfile', metavar='arquivo.json', help='configuration file')

	return parser.parse_args()


def config_parser_json(args):

	with open(args.configfile, 'r') as config:
		parsed_json = json.load(config)

		includes.build_processors(parsed_json['processors'])
		includes.build_platform(parsed_json['platform'])	



def main():
	args    = command_line_handler()    
	nightly = config_parser_json(args)
	
	 
if __name__ == '__main__':
	main()  