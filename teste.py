import json, argparse, re, os, shutil
from configparser     import ConfigParser

processor_base = ""

# Gerando o caminho ate o script Python
ROOT = os.path.dirname(os.path.abspath(__file__))

def command_line_handler():
	parser = argparse.ArgumentParser()
	parser.add_argument('configfile', metavar='arquivo.json', help='configuration file')
	return parser.parse_args()

def build_processors(procs):

	global processor_base

	src = os.path.join(ROOT, 'processors/'+ processor_base + '-base')	
	
	srcs = []	
	path_all_processors = "temp"

	for proc in procs:

		print("Building %s" % (proc["nome"]))

		dst = os.path.join(ROOT, 'processors/temp-'+proc["nome"])
		path_all_processors = path_all_processors + "-" +proc["nome"]
		srcs.append(dst)
		shutil.copytree(src, dst)

		for file in os.listdir(dst):
			if file.startswith(processor_base):

				arq = open(dst +'/'+ file, 'r')
				texto = arq.read()
				arq.close()

				texto = texto.replace(processor_base, proc["nome"])
				texto = texto.replace(processor_base.upper(), proc["nome"].upper())

				arq = open(dst +'/'+ file, 'w')
				arq.write(texto)
				arq.close()

				new_name = file.replace(processor_base, proc["nome"])
				os.rename(dst +'/'+ file, dst +'/'+new_name)

	src = os.path.join(ROOT, 'processors/'+ path_all_processors)	
	os.makedirs(src)
	
	for d in srcs:
		for file in os.listdir(d):
			if file != "powersc":
				shutil.copy2(d+'/'+file, src)

def build_platform(platform):
	global processor_base

	processor_base = platform["proc_base"]
	#print(proc_base)
	#print(platform["interconection"])

def config_parser_json(args):

	with open(args.configfile, 'r') as config:
		parsed_json = json.load(config)

		build_platform(parsed_json['platform'])
		build_processors(parsed_json['processors'])
		

def main():
	args    = command_line_handler()    
	config_parser_json(args)
	
	 
if __name__ == '__main__':
	main()  