 # @file      MPSoCTester.py
 # @author    Thiago Rodrigues de Oliveira
 #            troliveiraa@gmail.com

 #            Faculdade de Computação 
 #            FACOM-UFMS
 #            http://www.facom.ufms.br/

 # @version   1.0
 # @date      Thu, 4 May 2017 
 
 
 # This program is free software; you can redistribute it and/or modify 
 # it under the terms of the GNU General Public License as published by 
 # the Free Software Foundation; either version 2 of the License, or 
 # (at your option) any later version. 
 
 # This program is distributed in the hope that it will be useful, 
 # but WITHOUT ANY WARRANTY; without even the implied warranty of 
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 # GNU General Public License for more details. 
 
 # You should have received a copy of the GNU General Public License 
 # along with this program; if not, write to the Free Software 
 # Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
import os, shutil, sys, subprocess


class Controller:

	ROOT 			= "" # Caminho ate o script
	processor_base 	= "" # Processador usado como base para geracao dos cores
	processors 		= [] # Conjunto de processadores com suas caracteristicas
	n_cores 		= {} #
	tot_n_cores 	= 0  # Quantidade total de cores
	interconection 	= "" # noc, router
	timing 			= "" # at, lt
	benchmark 		= "" # Aplicacao que a plataforma ira simular
	power 			= "" # Medir consumo (true ou false)
	all_processors 	= "" # nome dos processadores para geracao do makefile
	rundirname 		= ""



	def __init__(self, root, platform, processors):

		self.ROOT 				= root
		self.processors 		= processors
		self.set_platform(platform)



	def set_platform(self, platform):
		self.processor_base		= platform["proc_base"]
		self.interconection 	= platform["interconection"]
		self.timing 			= platform["timing"]
		self.benchmark 			= platform["benchmark"]
		self.power 				= platform["power"]
		self.n_cores 			= dict(platform["n_cores"])

		for key in self.n_cores:
			# pega conteudo da chave ou seja o inteiro em si
			# que eh a qtd de processadores com essa chave
			self.tot_n_cores += int(self.n_cores[key]) 

	def set_rundirname(self):
		self.rundirname = self.all_processors.replace(' ', '.') + "." + \
						self.interconection + "." + self.timing + "." + \
						str(self.tot_n_cores) + "." + \
						self.benchmark
		self.rundirname = self.rundirname.replace('..', '.')


	def print_values(self):
		print("root: " + self.ROOT)
		print("proc_base: " + self.processor_base)
		print(self.interconection)
		print(self.timing)
		print(self.benchmark)
		print(self.power)
		print(self.n_cores)
		print(self.tot_n_cores)
		print(self.rundirname)

		print(self.makefile(self.processor_base, \
							self.all_processors, \
							str(self.tot_n_cores), \
							self.benchmark, \
							"", \
							self.interconection + "." + self.timing, \
							"mips.noc.het.at.4.dijkstra"))

		#print(self.processors)

	def build_transport_processor(self, processor):
		txt = '\n \
AC_ARCH(' + processor["name"] + '){ \n\
	ac_tlm2_port   MEM:'+ str(processor["memsize"]) +'M; \n \
	\n\
	'+ self.build_cache("IC_cache", processor["IC_cache"]) +' \n\
	'+ self.build_cache("DC_cache", processor["DC_cache"]) +' \n\
	\n \
	ac_tlm2_intr_port intr_port; \n\
	\n \
	ac_reg id; \n\
	ac_regbank RB:'+ str(processor["RB"]) +'; \n\
	ac_reg npc; \n\
	ac_reg hi, lo; \n\
	\n\
	ac_wordsize '+ str(processor["wordsize"]) +'; \n\
	ac_fetchsize '+ str(processor["fetchsize"]) +'; \n\
	\n\
	ARCH_CTOR(' + processor["name"] + ') { \n\
		ac_isa("' + processor["name"] + '_isa.ac"); \n\
		set_endian("big"); \n\
		IC.bindTo(MEM); \n\
		DC.bindTo(MEM); \n\
	}; \n \
}; \n'
		return txt

	def build_cache(self, type, cache):

		if type == "IC_cache":
			txt = '\
ac_icache IC("'+ cache["associativity"] +'", \
'+ str(cache["number_of_blocks"]) +', \
'+ str(cache["block_size"]) +', \
"'+ cache["write_policy"] +'", \
"'+ cache["replacement_policy"] +'");\
			'
		elif type == "DC_cache":
			txt = '\
ac_dcache DC("'+ cache["associativity"] +'", \
'+ str(cache["number_of_blocks"]) +', \
'+ str(cache["block_size"]) +', \
"'+ cache["write_policy"] +'", \
"'+ cache["replacement_policy"] +'");\
			'			
		else:
			txt = ''
		return txt

	# generate_processors possui a seguinte rotina: para cada processador descrito 
	# no arquivo de configuracao json, entra na pasta processor/ do MPSoCBench e 
	# e faz copia da pasta do processador base em seguida renomeia essa pasta de acordo
	# com o nome do processador do campo "name" do arquivo de configuracao json. Entra
	# nessa pasta e para todos os arquivos que o nome inicia com o nome do processador 
	# base substitui essa subcadeia pelo campo "name" do processador descrito no arquivo 
	# de configuracao json. Alem disso entra em todos os arquivos dessa pasta e troca 
	# toda a substring que é igual a processor base pelo campo "name" do processador
	# descrito no arquivo de configuracao json.

	def generate_processors(self):

		src = os.path.join(self.ROOT, 'processors/' + self.processor_base + '-base')	
		
		srcs = []	
		path_all_processors = "temp"

		for proc in self.processors:

			print("Building %s" % (proc["name"]))

			print(self.build_transport_processor(proc))

			self.all_processors +=  proc["name"] + " " 

			dst = os.path.join(self.ROOT, 'processors/temp-'+ proc["name"])
			path_all_processors = path_all_processors + "-" + proc["name"]
			srcs.append(dst)
			shutil.copytree(src, dst)

			for file in os.listdir(dst):
				if file.startswith(self.processor_base):

					arq = open(dst +'/'+ file, 'r')
					texto = arq.read()
					arq.close()

					texto = texto.replace(self.processor_base, proc["name"])
					texto = texto.replace(self.processor_base.upper(), proc["name"].upper())

					arq = open(dst +'/'+ file, 'w')
					arq.write(texto)
					arq.close()

					new_name = file.replace(self.processor_base, proc["name"])
					os.rename(dst +'/'+ file, dst +'/'+new_name)

		src = os.path.join(self.ROOT, 'processors/'+ path_all_processors)	
		os.makedirs(src)
		
		for d in srcs:
			for file in os.listdir(d):
				if file != "powersc":
					shutil.copy2(d+'/'+file, src)

		self.set_rundirname()
		

	def cmd_exists(self, cmd):
		return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

	def makefile(self, proc_base, proc, nproc, sw, power, intercon, plat_rundir):

		make = "#FILE GENERATED AUTOMAGICALLY - DO NOT EDIT"
		make = make + \
				"\nexport SHELL := /bin/bash"  \
				"\nexport PROCESSOR_BASE := " + proc_base +  \
				"\nexport PROCESSOR := " + proc +  \
				"\nexport NUMPROCESSORS := " + nproc + \
				"\nexport SOFTWARE := " + sw + \
				"\nexport PLATFORM := platform." + intercon + "\n" 	

		if proc_base == 'arm':
			cross = proc_base + "-newlib-eabi-gcc"
			if self.cmd_exists( cross ):
				make = make + "export CROSS := " + cross + "\n"
			else:
				sys.exit('\nERROR: Cross-compiler ' + cross + ' is not in the PATH\n')
		else:
			cross = proc_base + "-newlib-elf-gcc"
			if self.cmd_exists( cross ):
				make = make + "export CROSS := " + proc_base + "-newlib-elf-gcc\n"
			else:
				sys.exit('\nERROR: Cross-compiler ' + cross + ' is not in the PATH\n')

		# for older compilers
		#make = make + "\nexport CROSS := " + proc + "-elf-gcc\n"
		if power:
			pw_flag = " -pw"
			make = make + "export POWER_SIM_FLAG := -DPOWER_SIM=\\\"\\\"\n"
		else:
			pw_flag = ""
			make = make + "export POWER_SIM_FLAG := \n" 

		make = make + "export ACSIM_FLAGS := -abi -ndc " + pw_flag + "\n"; 
		
		if intercon == 'noc.at':
			make = make + "export WAIT_TRANSPORT_FLAG := -DWAIT_TRANSPORT\nexport TRANSPORT := nonblock\n"
		else:
			make = make + "export WAIT_TRANSPORT_FLAG := \nexport TRANSPORT := block\n"
		make = make + "export MEM_SIZE_DEFAULT := -DMEM_SIZE=536870912\n"
		make = make + "export RUNDIRNAME := " + plat_rundir + "\n"
		if proc != 'arm':
			make = make + "export ENDIANESS := -DAC_GUEST_BIG_ENDIAN\n"
		else: 
			make = make + "export ENDIANESS := \n"

		#make = make + "ifeq ($(PROCESSOR),arm)\nexport CFLAGS_AUX := -DPROCARM\nendif\n"
		#make = make + "ifeq ($(PROCESSOR),mips)\nexport CFLAGS_AUX := -DPROCMIPS\nendif\n"
		#make = make + "ifeq ($(PROCESSOR),sparc)\nexport CFLAGS_AUX := -DPROCSPARC\nendif\n"
		#make = make + "ifeq ($(PROCESSOR),powerpc)\nexport CFLAGS_AUX := -DPROCPOWERPC\nendif\n"
		
		make = make + "include Makefile.rules\n"
		return make