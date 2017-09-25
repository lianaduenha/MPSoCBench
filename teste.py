import json, argparse, re, os, shutil
from configparser     import ConfigParser

from modules.controller import Controller

# Gerando o caminho ate o script Python
ROOT = os.path.dirname(os.path.abspath(__file__))

def command_line_handler():
	parser = argparse.ArgumentParser()
	parser.add_argument('configfile', metavar='arquivo.json', help='configuration file')
	return parser.parse_args()



def config_parser_json(args):

	with open(args.configfile, 'r') as config:
		parsed_json = json.load(config)


		controller = Controller(ROOT, parsed_json['platform'], parsed_json['processors'])
		controller.generate_processors()
		controller.print_values()

		#build_platform(parsed_json['platform'])
		#build_processors(parsed_json['processors'])
		

def main():
	args    = command_line_handler()    
	config_parser_json(args)
	
	 
if __name__ == '__main__':
	main()  