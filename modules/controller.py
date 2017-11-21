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
	power 			= False # Medir consumo (true ou false)
	all_processors 	= "" # nome dos processadores para geracao do makefile
	rundirname 		= ""
	folder 			= ""
	name_plat 		= ""
	clean 			= True
	metrics			= ""



	def __init__(self, root, platform, processors, clean):

		self.ROOT 				= root
		self.processors 		= processors
		self.clean 				= clean
		self.set_platform(platform)



	def set_platform(self, platform):
		self.processor_base		= platform["proc_base"]
		self.interconection 	= platform["interconection"]
		self.timing 			= platform["timing"]
		self.benchmark 			= platform["benchmark"]
		self.metrics			= platform["metrics"]
		self.power 				= self.metrics["power"]
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
		# print("root: " + self.ROOT)
		# print("proc_base: " + self.processor_base)
		# print(self.interconection)
		# print(self.timing)
		# print(self.benchmark)
		# print(self.power)
		# print(self.n_cores)
		# print(self.tot_n_cores)
		# print(self.rundirname)

		self.makefile(self.folder, \
							self.processor_base, \
							self.all_processors, \
							str(self.tot_n_cores), \
							self.benchmark, \
							"", \
							self.interconection + "." + self.timing, \
							"")

		self.write_in_file(self.ROOT+'/', "Makefile", self.makefile(self.folder, \
							self.processor_base, \
							self.all_processors, \
							str(self.tot_n_cores), \
							self.benchmark, \
							"", \
							self.interconection + "." + self.timing, \
							"mips.noc.het.at.4.dijkstra"))

		self.build_makefile_1(self.processors)

		self.write_in_file(self.ROOT + '/processors/' + self.folder + '/', \
			                "Makefile_1", \
			                self.build_makefile_1(self.processors))

		self.build_platform()
		
		self.execution()

		if self.clean:
			self.remove_files_temp()


	def remove_files_temp(self):

		if os.path.exists(self.ROOT+"/platforms/temp." + self.name_plat):
			os.system("rm -R " + self.ROOT+"/platforms/temp." + self.name_plat)
		if os.path.exists(self.ROOT+"/processors/" + self.folder):
			os.system("rm -R " + self.ROOT+"/processors/" + self.folder)


	def build_platform(self):
		if len(self.n_cores) > 1:
			if self.interconection + "." + self.timing == "router.lt":
				txt = self.build_platform_het_router_lt()
				dst = self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/"
				os.system("cd "+ self.ROOT + "/platforms/ && mkdir " + "temp."+ self.name_plat)
				os.system("cp " + self.ROOT + "/platforms/platform.router.lt/Makefile " + self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/")
				os.system("cp " + self.ROOT + "/platforms/platform.router.lt/defs.arp " + self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/")
				self.write_in_file(dst, "main.cpp", txt)
				return txt
			elif self.interconection + "." + self.timing == "noc.lt":
				txt = self.build_platform_het_noc_lt()
				dst = self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/"
				os.system("cd "+ self.ROOT + "/platforms/ && mkdir " + "temp."+ self.name_plat)
				os.system("cp " + self.ROOT + "/platforms/platform.noc.lt/Makefile " + self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/")
				os.system("cp " + self.ROOT + "/platforms/platform.noc.lt/defs.arp " + self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/")
				self.write_in_file(dst, "main.cpp", txt)
				return txt
			else:
				txt = self.build_platform_het_noc_at()
				dst = self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/"
				os.system("cd "+ self.ROOT + "/platforms/ && mkdir " + "temp."+ self.name_plat)
				os.system("cp " + self.ROOT + "/platforms/platform.noc.at/Makefile " + self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/")
				os.system("cp " + self.ROOT + "/platforms/platform.noc.at/defs.arp " + self.ROOT + "/platforms/" + "temp."+ self.name_plat +"/")
				self.write_in_file(dst, "main.cpp", txt)
				return txt
		else:
			return " "

	def build_csv_processor(self):

		for proc in self.processors:

			file = open(self.ROOT + "/processors/"+ self.folder +"/" + proc["name"] +".H", 'r')
			txt = file.read()
			file.close()

			l = txt.split('#ifdef POWER_SIM', 1)

			
			if self.metrics[proc["name"]+"_power_table"] == "":
				csv = '\
\n // #ifdef POWER_SIM \
\n // #define POWER_TABLE_FILE "acpower_table_mips_ASIC_freepdk45_50_125_250_400Mhz.csv" \n\
#include "arch_power_stats.H"'
			else:
				csv = '\
\n //#ifdef POWER_SIM \
\n //#define POWER_TABLE_FILE "' + self.metrics[proc["name"]+"_power_table"] + '" \n\
#include "arch_power_stats.H"' 
			
			r = l[1].split('#include "arch_power_stats.H"', 1)

			#pwr_st = "power_stats"
			#pwr_st_r = "power_stats_" + proc["name"]

			#t = r[1].replace(pwr_st, pwr_st_r)

			txt = l[0] + csv + t

			file = open(self.ROOT + "/processors/"+ self.folder +"/" + proc["name"] +".H", 'w')
			file.write(txt)
			file.close()



	def execution(self):

		#os.system("make clean_het distclean_het run_het")

		os.system("make clean_het distclean_het procs")

		#if self.power:
			#self.build_csv_processor()

		os.system("make run_het")



		# path = "rundir/" + plat_rundir
		# print "Creating rundir for " + path[7:] + "..."
		# # creates rundir for each platform
		# os.system("mkdir -p " + path)
		# # copies it to its rundir                    
		# os.system("make copy")
		# os.system("make clean")

	def write_in_file(self, dst, file_name, txt):
		file = open( dst + file_name, 'w')
		file.write(txt)
		file.close()


	def build_description_processor(self, processor):
		txt = '\n \
AC_ARCH(' + processor["name"] + '){ \n \
	'+ self.build_timing() +' MEM:'+ str(processor["memsize"]) +'M; \n \
	\n \
	'+ self.build_cache("IC_cache", processor["IC_cache"]) +' \n \
	'+ self.build_cache("DC_cache", processor["DC_cache"]) +' \n \
	\n \
	ac_tlm2_intr_port intr_port; \n \
	\n \
	'+ self.build_ac_regs(processor) +'\
	\n \
	ac_wordsize '+ str(processor["wordsize"]) +'; \n \
	ac_fetchsize '+ str(processor["fetchsize"]) +'; \n \
	ac_frequency '+ str(processor["frequency"]) +'; \n \
	\n \
	ARCH_CTOR(' + processor["name"] + ') { \n \
		ac_isa("' + processor["name"] + '_isa.ac"); \n \
		set_endian("' + processor["endianness"] + '"); \n \
		IC.bindTo(MEM); \n \
		//DC.bindTo(MEM); \n \
	}; \n \
}; \n'
		return txt


	def build_ac_regs(self, proc):
		if self.processor_base == 'mips':
			txt = '\n \
	ac_reg id; \n \
	ac_regbank RB:'+ str(proc["regbank_1"]) +'; \n \
	ac_reg npc; \n \
	ac_reg hi, lo; \n \
			'

		elif self.processor_base == 'sparc':
			txt = '\n \
	ac_regbank RB:'+ str(proc["regbank_1"]) +'; \n \
	ac_regbank REGS:'+ str(proc["regbank_2"]) +'; \n \
\n \
	ac_reg npc; \n \
\n \
	ac_reg<1> PSR_icc_n; \n \
	ac_reg<1> PSR_icc_z;\n \
	ac_reg<1> PSR_icc_v;\n \
	ac_reg<1> PSR_icc_c;\n \
\n \
	ac_reg PSR;\n\
	ac_reg Y;\n \
\n \
	ac_reg<8> WIM;\n \
	ac_reg<8> CWP;\n \
\n \
	ac_reg id;\n \
			'

		elif self.processor_base == 'powerpc':
			txt = '\n \
	ac_reg id; \n \
	ac_regbank GPR:'+ str(proc["regbank_1"]) +'; \n \
\
	ac_reg SPRG4; \n \
	ac_reg SPRG5; \n \
	ac_reg SPRG6;\n \
	ac_reg SPRG7;\n \
	ac_reg USPRG0;\n \
\
	ac_reg XER;\n \
\
	ac_reg MSR;\n \
\
	// sc instruction not tested/used \n \
	ac_reg EVPR;\n \
	ac_reg SRR0;\n \
	ac_reg SRR1;\n \
\
	ac_reg CR;\n \
	ac_reg LR;\n \
	ac_reg CTR;\n \
			'

		else:
			txt = '\n \
	ac_regbank RB:'+ str(proc["regbank_1"]) +';\n \
\
	ac_reg R14_irq, R14_fiq, R14_svc, R14_abt, R14_und, R13_irq, R13_svc; \n \
	ac_reg R13_abt, R13_und, R13_fiq;\n \
	ac_reg SPSR_irq, SPSR_fiq, SPSR_svc, SPSR_abt, SPSR_und;\n \
	// FIQ private regs \n \
	ac_reg R12_fiq, R11_fiq, R10_fiq, R9_fiq, R8_fiq; \n \
\
	ac_reg id; \
			'

		return txt

	def build_timing(self):

		if self.timing == "lt":
			txt = 'ac_tlm2_port'
		elif self.timing == "at":
			txt = 'ac_tlm2_nb_port'
		else:
			txt = ''

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
//ac_dcache DC("'+ cache["associativity"] +'", \
'+ str(cache["number_of_blocks"]) +', \
'+ str(cache["block_size"]) +', \
"'+ cache["write_policy"] +'", \
"'+ cache["replacement_policy"] +'");\
			'			
		else:
			txt = ''
		return txt


	def build_makefile_1(self, procs):

		ACSRCS 	= ''
		ACINCS 	= ''
		ACHEAD 	= ''
		SRCS 	= 'main.cpp $(ACSRCS) '
		CPPs	= ''
		COPY 	= ''
		pwrsc = ''
		cfl = ''

		if self.power:
			pwrsc = '`pkg-config --libs powersc`'
			cfl = ' -DPOWER_SIM=\\"$(PWD)/powersc\\"'
		else:
			pwrsc = ''

		for proc in procs:

			ACSRCS 	+= proc["name"] + '_arch.cpp ' + proc["name"] + '_arch_ref.cpp ' + proc["name"] + '.cpp '
			ACHEAD 	+= proc["name"] + '_parms.H ' + proc["name"] + '_arch.H ' + proc["name"] + '_arch_ref.H ' + proc["name"] + '_isa.H ' + proc["name"] + '_bhv_macros.H ' + proc["name"] + '_intr_handlers.H ' + proc["name"] + '_ih_bhv_macros.H ' + proc["name"] + '.H '
			SRCS 	+= proc["name"] + '_syscall.cpp ' + proc["name"] + '_intr_handlers.cpp '

			CPPs += proc["name"] + '.cpp '

			COPY += '\n\
# Copy from template if ' + proc["name"] + '_syscall.H not exist \n\
' + proc["name"] + '_syscall.H: \n\
	cp ' + proc["name"] + '_syscall.H.tmpl ' + proc["name"] + '_syscall.H \n\
\n\
# Copy from template if ' + proc["name"] + '_intr_handlers.cpp not exist \n\
' + proc["name"] + '_intr_handlers.cpp:\n\
	cp ' + proc["name"] + '_intr_handlers.cpp.tmpl ' + proc["name"] + '_intr_handlers.cpp '


		txt = '\
INC_DIR := -I. `pkg-config --cflags systemc` `pkg-config --cflags archc` `pkg-config --cflags tlm`\n\
LIB_SYSTEMC := `pkg-config --libs systemc`\n\
LIB_ARCHC := `pkg-config --libs archc`\n\
LIB_POWERSC :='+pwrsc+'\n\
LIB_DWARF :=\n\
LIBS := $(LIB_SYSTEMC) $(LIB_ARCHC) $(LIB_POWERSC) $(LIB_DWARF) -lm $(EXTRA_LIBS)\n\
CC :=   g++\n\
OPT :=   -O3\n\
DEBUG :=   -g\n\
OTHER := -std=c++11  -DAC_GUEST_BIG_ENDIAN  -Wno-deprecated\n\
CFLAGS := $(DEBUG) $(OPT) $(OTHER) '+cfl+'\n\
\n\
TARGET := ' +self.processor_base +'\n\
\n\
# These are the source files automatically generated by ArchC, that must appear in the SRCS variable \n\
ACSRCS := '+ ACSRCS +'\n\
\n\
# These are the source files automatically generated  by ArchC that are included by other files in ACSRCS \n\
ACINCS := $(TARGET)_isa_init.cpp\n\
\n\
# These are the header files automatically generated by ArchC \n\
ACHEAD := '+ ACHEAD +'\n\
\n\
# These are the library files provided by ArchC\n\
# They are stored in the archc/lib directory\n\
ACLIBFILES := ac_decoder_rt.o ac_module.o ac_mem.o ac_utils.o  ac_syscall.o ac_tlm2_port.o ac_tlm2_intr_port.o \n\
\n\
# These are the source files provided by the user + ArchC sources\n\
SRCS := '+ SRCS +'\n\
\n\
OBJS := $(SRCS:.cpp=.o)\n\
\n\
EXE := $(TARGET).x\n\
\n\
.SUFFIXES: .cc .cpp .o .x\n\
\n\
all:  lib\n\
\n\
$(EXE): $(OBJS)\n\
	$(CC) $(CFLAGS) $(INC_DIR) $(LIB_DIR) -o $@ $(OBJS) $(LIBS) 2>&1 | c++filt\n\
\n\
# Copy from template if main.cpp not exist\n\
main.cpp:\n\
	cp main.cpp.tmpl main.cpp\n\
\n\
'+ COPY +'\n\
\n\
lib: '+ CPPs + ' $(OBJS)\n\
	ar r lib$(TARGET).a $(OBJS)\n\
\n\
.cpp.o:\n\
	$(CC) $(CFLAGS) $(INC_DIR) -c $<\n\
\n\
.cc.o:\n\
	$(CC) $(CFLAGS) $(INC_DIR) -c $<\n\
\n\
clean:\n\
	rm -f $(OBJS) *~ $(EXE) core *.o *.a\n\
\n\
model_clean:\n\
	rm -f $(ACSRCS) $(ACHEAD) $(ACINCS) *.tmpl loader.ac\n\
\n\
sim_clean: clean model_clean\n\
\n\
distclean: sim_clean\n\
	rm -f main.cpp Makefile'
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

		#src = os.path.join(self.ROOT, 'processors/' + self.processor_base + '-base')
		src = os.path.join(self.ROOT, 'processors/' + self.processor_base)
		a = src	
		
		srcs = []	
		path_all_processors = "temp"

		for proc in self.processors:

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

					if file == "mips_syscall.cpp":
						texto = texto.replace("procNumber", "procNumber" + proc["name"])


					arq = open(dst +'/'+ file, 'w')
					arq.write(texto)
					arq.close()

					new_name = file.replace(self.processor_base, proc["name"])
					os.rename(dst +'/'+ file, dst +'/'+new_name)

				# if file == "arch_power_stats.H":
				# 	arq = open(dst +'/'+ file, 'r')
				# 	texto = arq.read()
				# 	arq.close()

				# 	pwr_st = "class power_stats"
				# 	pwr_st_r = "class power_stats_" + proc["name"]

				# 	texto = texto.replace(pwr_st, pwr_st_r)

				# 	pwr_st = "power_stats("
				# 	pwr_st_r = "power_stats_" + proc["name"] + "("

				# 	texto = texto.replace(pwr_st, pwr_st_r)


				# 	#texto = texto.replace(pwr_st.upper(), pwr_st_r.upper())

				# 	arq = open(dst +'/'+ file, 'w')
				# 	arq.write(texto)
				# 	arq.close()

				# 	new_name = "arch_power_stats_" + proc["name"] + ".H"
				# 	os.rename(dst +'/'+ file, dst +'/'+new_name)



			#gera o arquivo de descricao do processador (ex; mips.ac mipsnoblock, mipsblock)
			# sera uma descricao unica apartir de agora

			
			self.write_in_file(dst + '/',\
								proc["name"] + ".ac", \
								self.build_description_processor(proc))

		self.folder = path_all_processors

		src = os.path.join(self.ROOT, 'processors/' + path_all_processors)	

		if os.path.exists(src):
			
			while True:
				#op = sys.stdin.readline()

				op = input('\
You have decided not to delete temporary files and folders \n\
from the last simulation. You need to delete these files. \n\
Do you want to delete now? (Y / n)')

				if op == 'Y':
					for folder in os.listdir(self.ROOT+"/platforms/"):
						if folder.startswith("temp."):
							os.system("rm -R " + self.ROOT+"/platforms/"+ folder)

					os.system("rm -R " + src)
					break
				elif op == 'n':
					#remove as pastas de processadores temporario
					for proc in self.processors:
						if os.path.exists(self.ROOT+"/processors/temp-" + proc["name"]):
							os.system("rm -R " + self.ROOT+"/processors/temp-" + proc["name"])
					quit()
				else:
					print("Press (Y/n)")

		
		os.makedirs(src)
		flag = 0
		for d in srcs:
			for file in os.listdir(d):
				if file != "powersc":
					shutil.copy2(d+'/'+file, src)


		os.system("cp -R " + a + "/powersc/ " + src + "/powersc")

		#remove as pastas de processadores temporario
		for proc in self.processors:
			if os.path.exists(self.ROOT+"/processors/temp-" + proc["name"]):
				os.system("rm -R " + self.ROOT+"/processors/temp-" + proc["name"])

		self.set_rundirname()
		

	def cmd_exists(self, cmd):
		return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

	def makefile(self, folder, proc_base, proc, nproc, sw, power, intercon, plat_rundir):

		if len(self.n_cores) > 1:
			self.name_plat = "platform." + self.interconection + ".het." + self.timing
			#plat_rundir = proc_base + "." + self.interconection + ".het." + self.timing + str
		else:
			self.name_plat = "platform." + self.interconection + "." + self.timing



		make = "#FILE GENERATED AUTOMAGICALLY - DO NOT EDIT"
		make = make + \
				"\nexport SHELL := /bin/bash"  \
				"\nexport FOLDER := " + folder +  \
				"\nexport PROCESSOR_BASE := " + proc_base +  \
				"\nexport PROCESSOR := " + proc +  \
				"\nexport NUMPROCESSORS := " + nproc + \
				"\nexport SOFTWARE := " + sw + \
				"\nexport PLATFORM := " + self.name_plat + "\n" 	

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
		if self.power:
			pw_flag = " -pw"
			make = make + "export POWER_SIM_FLAG := -DPOWER_SIM=\\\"\\\"\n"
		else:
			pw_flag = ""
			make = make + "export POWER_SIM_FLAG := \n" 
		# pw_flag = "-pw"
		# make = make + "export POWER_SIM_FLAG := \n" 

		make = make + "export ACSIM_FLAGS := -abi -ndc " + pw_flag + "\n"; 
		
		if intercon == 'noc.at':
			make = make + "export WAIT_TRANSPORT_FLAG := -DWAIT_TRANSPORT\nexport TRANSPORT := nonblock\n"
		else:
			make = make + "export WAIT_TRANSPORT_FLAG := \nexport TRANSPORT := block\n"
		make = make + "export MEM_SIZE_DEFAULT := -DMEM_SIZE=536870912\n"
		make = make + "export RUNDIRNAME := " + self.rundirname + "\n"
		if proc != 'arm':
			make = make + "export ENDIANESS := -DAC_GUEST_BIG_ENDIAN\n"
		else: 
			make = make + "export ENDIANESS := \n"

		make = make + "ifeq ($(PROCESSOR_BASE),arm)\nexport CFLAGS_AUX := -DPROCARM\nendif\n"
		make = make + "ifeq ($(PROCESSOR_BASE),mips)\nexport CFLAGS_AUX := -DPROCMIPS\nendif\n"
		make = make + "ifeq ($(PROCESSOR_BASE),sparc)\nexport CFLAGS_AUX := -DPROCSPARC\nendif\n"
		make = make + "ifeq ($(PROCESSOR_BASE),powerpc)\nexport CFLAGS_AUX := -DPROCPOWERPC\nendif\n"
		
		make = make + "include Makefile.rules\n"
		return make






















	def build_defines(self, defines):


			file = open(self.ROOT + "/defines.h", 'r')
			txt = file.read()
			file.close()

			# l = txt.split('#define _DEFINES_H', 1)
			# d = '\n#define _DEFINES_H\n' + defines
			# txt = l[0] + d + l[1]

			txt = '\
/******************************************************************************\n\
 * @file      defines.h\n\
 * @author    Liana Duenha\n\
 *\n\
 * @author    The ArchC Team\n\
 *            http://www.archc.org/\n\
 *\n\
 *            Computer Systems Laboratory (LSC)\n\
 *            IC-UNICAMP\n\
 *            http://www.lsc.ic.unicamp.br/\n\
 * \n\
 * @date      01, Feb, 2013\n\
 * @brief     Defines the ArchC TLM 2.0  port.\n\
\n\
 *\n\
 * @attention Copyright (C) 2002-2012 --- The ArchC Team\n\
 *\n\
 *******************************************************************************/\n\
\n\
#ifndef _DEFINES_H \n\
#define _DEFINES_H	\n\
\n\
// PLATFORM STATIC PARAMETERS\n\
#define LOCAL_FILE_MEASURES_NAME "local_report.txt"\n\
#define GLOBAL_FILE_MEASURES_NAME "../../global_report.txt"\n\
\n\
#define MAX_WORKERS 64 	/* This is a arbitrary limit for the number of processors. If necessary, this value can be modified, but\n\
 there is no guarantee that all applications will work properly */\n\
\n\
// NOC and Router STATIC PARAMETERS\n\
#define MAX_LINES 72\n\
#define MAX_COLUMNS 3 \n\
#define ON 1\n\
#define OFF 0\n\
#define SIZE_OF_BUFFER_PACKAGES 2000\n\
\n\
 // These parameters define the address space for IPs\n\
// We consider that memory address space is from 0 to 0x20000000-1\n\
// The address to access the Lock IP is 0x20000000\n\
// The address to access the DVFS IP is 0x21000000\n\
// The address to access the INTR_CTRL IP is 0x22000000\n\
// The address to access the DIR IP is 0x23000000\n\
// Next, we use a DELTA_IP_ADDRESS = 0x100 as a default value\n\
// If you want to update these values, be carefull maintaining the coherency with the tlm_router, tlm_noc_at and tlm_noc_lt\n\
// routing definitions (see is/tlm_router, is/tlm_noc_lt, is/tlm_noc_at)\n\
#define BASE_MEMORY_ADDRESS 536870912 // 0x20000000 -  last memory byte address is 536870911\n\
\n\
#define LOCK_ADDRESS        0x20000000\n\
#define INTR_CTRL_ADDRESS   0X21000000\n\
#define DIR_ADDRESS         0x22000000\n\
#define DFS_ADDRESS         0x23000000\n\
#define DELTA_IP_ADDRESS    0x00000100\n\
#define DELTA               16777216  // 16^6 = 0x1000000\n\
\n\
//#define DRAMSIM2\n\
\n\
// DEBUG FLAGS\n\
#define NOC_DEBUG       0\n\
#define LOCK_DEBUG      0\n\
#define MEMORY_DEBUG    0\n\
#define ROUTER_DEBUG    0\n\
#define DFS_DEBUG       0\n\
#define INTR_CTRL_DEBUG 0\n\
\n\
// ROUTER STATIC PARAMETERS\n\
\n\
// TLM2 PAYLOAD STATIC PARAMETERS\n\
// Define the transaction direction\n\
#define FORWARD  0\n\
#define BACKWARD 1\n\
\n\
// TIMING STATIC PARAMETERS\n\
#define TIME_MEMORY    100\n\
#define TIME_DIR       20\n\
#define TIME_NODE      6\n\
#define TIME_ROUTER    20\n\
#define TIME_LOCK      20\n\
#define TIME_DFS       20\n\
#define TIME_INTR_CTRL 20\n\
\n\
// DVFS STATIC PARAMETERS\n\
// The definition of the power states depends on how the software (application) will explore this feature\n\
// By default, the acPthread will use just the states LOW and HIGH. So, if you want to enable DVFS with this two \n\
// power states, you must define the "id" that you want for each one of this states (based on the power table that you will use \n\
// see processor/mips/ac_power_stats.H or processors/sparc/ac_power_stats.H to know more about this)\n\
// In case you define different power states here, you must also update the acPthread library to use them (sw/acPthread.c).\n\
\n\
// But if you want to desable DFS (using just a single power state), use HIGH=LOW=0\n\
\n\
#define HIGH 3\n\
#define LOW 0\n\
#define INITIAL_PW_STATE 0\n\
\n\
//#define DFS_AUTO_SELECTION_CPU_RATE\n\
//#define DFS_AUTO_SELECTION_ENERGY_STAMP\n\
#define FIRST_DELTA_T 0.025   // 50*0,0005\n\
#define DELTA_T 0.00025\n\
#define N_DELTA_T 50\n\
\n\
#ifdef PROCMIPS \n\
'+ defines +'\
#endif\n\
\n\
// NoC Hermes STATIC PARAMETERS - NOT IN USE IN THIS VERSION\n\
#define LOCAL_MEM_SIZE  67108864\n\
#define TEXTAREA	0x00d16f\n\
#endif			'

			file = open(self.ROOT + "/defines.h", 'w')
			file.write(txt)
			file.close()















































	def build_platform_het_noc_at(self):

		i = 1
		defines = '\
\n\
\n/*#ifdef POWER_SIM\
\n  #undef POWER_SIM\
\n  #define POWER_SIM "../../processors/'+self.folder+'/powersc" \
\n#endif*/\
\n\
		'
		var_cores = ''

		vectors = ''

		procs_interrupt = '\
\n    // Binding processors and interruption controller \
\n    int aux = 0;'

		bind_procs = 'int b = 0;\n '
		
		load_elfs = '\n\
\n    // Load elf before start\
\n    first_load = true; aux = 0;'
		
		init_s = ''

		print_s = ''

		printing_statistics = ''

		connect_power = ''

		connect_power_info = ''

		check_status = '\
\n    // Checking the status\
\n    bool status = 0;'



		for proc in self.processors:
			defines += '\
\n#include "../../processors/'+ self.folder +'/' + proc["name"] + '.H"\
\n#define PROCESSOR_NAME' + str(i) + ' '+ proc["name"] +' '
			if i == 1:
				defines += '\
\n#define PROCESSOR_NAME_parms '+ proc["name"] +'_parms\
\n\
				'
			else:
				defines += '\
\n#define PROCESSOR_NAME'+str(i)+'_parms '+ proc["name"] +'_parms\
\n\
				'
			var_cores += '\n  int N_CORES_'+str(i)+' = '+ str(self.n_cores[proc["name"]]) +';'

			vectors += '\n\
  vector<' + proc["name"] +' *> procs_'+ str(i) +';\n\
\n\
  for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\n\
    char name[10] = "proc";\n\
    char number_str[3];\n\
    sprintf(number_str, "%d", id);\n\
    strcat(name, number_str);\n\
    procs_'+ str(i) +'.push_back(new ' + proc["name"] +'(name, id));\n\
    (procs_'+ str(i) +'[i]->MEM_mport).setProcId(id);\n\
    id++;\n\
  }\n			'




			procs_interrupt +='\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      intr_ctrl.CPU_port[aux](procs_'+ str(i) +'[i]->intr_port);\
\n      aux++;\
\n    }\
\n\
			'

			bind_procs += '\
  while(b < procs_'+ str(i) +'.size()){\n\
\n\
    procs_'+ str(i) +'[b]->MEM.LOCAL_init_socket.bind(noc.wrapper[wrMS].LOCAL_target_socket);\n\
    noc.wrapper[wrMS].LOCAL_init_socket.bind(noc.slaveEmptyNodes[emptySlaves].LOCAL_slave_target_socket);\n\
    #ifdef POWER_SIM\n\
      //noc.wrapper[wrMS].initDFS(procs_'+ str(i) +'[b]);\n\
    #endif\n\
    wrMS++;\n\
    emptySlaves++;\n\
    noc.tableOfRouts.newEntry(line, column);\n\
    inc (line,column,r);\n\
    b++;\n\
  }\n\
  b = 0;\n\
			'

			load_elfs += '\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      load_elf<' + proc["name"] +'>(*procs_'+ str(i) +'[i], mem, arguments[aux][1], 0x000000, MEM_SIZE);\
\n      first_load = false; aux++;\
\n    }\
\n\
			'



			init_s += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->init(); // It passes the arguments to processors\
\n    }\
\n\
			'

			print_s +='\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->PrintStat();\
\n      procs_'+ str(i) +'[i]->FilePrintStat(global_time_measures);\
\n      procs_'+ str(i) +'[i]->FilePrintStat(local_time_measures);\
\n    }\
\n\
			'
			printing_statistics += '\
\n\
\n      for (i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.time = sc_simulation_time();\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.print();\
\n      }\
\n\
			'

			connect_power +='\n\
\n      /*for (i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ps.powersc_connect();\
\n        procs_'+ str(i) +'[i]->IC.powersc_connect();\
\n        procs_'+ str(i) +'[i]->DC.powersc_connect();\
\n        }*/\
\n \
			'
			connect_power_info += '\
\n\
\n      for (i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n          d += procs_'+ str(i) +'[i]->ps.getEnergyPerCore();\
\n\
			'

			check_status += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n      status = status + procs_'+ str(i) +'[i]->ac_exit_status;\
\n\
			'


			i += 1

		connect_power += '\
	  //noc.powersc_connect();\n\
     //procs_'+ str(i-1) +'[N_CORES_'+ str(i-1) +' - 1]->ps.report();\n\
		'

		#self.build_defines(defines)

		txt = '\
/********************************************************************************\n \
        MPSoCBench Benchmark Suite\n\
        Authors: Liana Duenha\n\
        Supervisor: Rodolfo Azevedo\n\
        Date: July-2012\n\
        www.archc.org/benchs/mpsocbench\n\
\n\
        Computer Systems Laboratory (LSC)\n\
        IC-UNICAMP\n\
        http://www.lsc.ic.unicamp.br/\n\
\n\
\n\
        This source code is part of the MPSoCBench Benchmark Suite, which is a free\n\
        source-code benchmark for evaluation of Electronic Systemc Level designs.\n\
        This benchmark is distributed with hope that it will be useful, but without \n\
        any warranty.\n\
\n\
*********************************************************************************/\n\
const char *project_name = "platform.noc.at";\n\
const char *project_file = "";\n\
const char *archc_version = "";\n\
const char *archc_options = "";\n\
\n\
#include <systemc.h>\n\
#include <sys/time.h>\n\
#include <stdlib.h>\n\
#include <stdio.h>\n\
#include <string.h>\n\
\n\
//#include "../../defines.h"\n\
#define SC_INCLUDE_DYNAMIC_PROCESSES\n\
\n\
#include "tlm_memory.h"\n\
#include "tlm_noc.h"\n\
#include "tlm_lock.h"\n\
#include "wrappers_noc.h"\n\
#include "tlm_dfs.h"\n\
\n\
#include "ac_utils.H"\n\
#include "ac_tlm_protocol.H"\n\
#include "tlm_intr_ctrl.h"\n\
//#include "tlm_diretorio.h"\n\
\n\
'+ defines +'\
\n\
//#define AC_DEBUG\n\
using user::tlm_memory;\n\
using user::tlm_noc;\n\
using user::tlm_lock;\n\
using user::wrapper_master_slave_to_noc;\n\
using user::tlm_intr_ctrl;\n\
//using user::tlm_diretorio;\n\
\n\
#ifdef POWER_SIM\n\
using user::tlm_dfs;\n\
#endif\n\
\n\
// Global variables\n\
int N_WORKERS;\n\
struct timeval startTime;\n\
struct timeval endTime;\n\
FILE *local_time_measures;\n\
FILE *global_time_measures;\n\
\n\
bool first_load;\n\
\n\
// Functions\n\
void report_start(char *, char *, char *);\n\
void report_end();\n\
template<class type_core> void load_elf(type_core &, tlm_memory &, char *, unsigned int, unsigned int);\n\
\n\
int inc (int &line, int &column, int &r)\n\
{\n\
  column = (column+1)%r;\n\
  if (column == 0) line++;\n\
}\n\
\n\
int sc_main(int ac, char *av[]) {\n\
\n\
  sc_report_handler::set_actions("/IEEE_Std_1666/deprecated", SC_DO_NOTHING);\n\
\n\
  /* Checking arguments */\n\
  int N_WORKERS;\n\
\n\
  if (ac != 0) {\n\
    N_WORKERS = atoi(av[2]);\n\
    if (N_WORKERS > MAX_WORKERS) {\n\
      printf("\\nThe amount of processors must be less than 64 %d.\\n", MAX_WORKERS);\n\
      exit(1);\n\
    }\n\
  }\n\
  else {\n\
    printf("\\nNo arguments for main.\\n");\n\
    exit(1);\n\
  }\n\
\n\
  ///************************************************************************************\n\
  // Creating platform components\n\
  //	- A memory with MEM_SIZE bytes\n\
  //	- A lock device\n\
  //	- A set of N_WORKERS processors\n\
  //	- A NoC with suficient nodes useful to communicate memory, lock and\n\
  //processors\n\
  //*************************************************************************************\n\
\n\
  int id = 0;\n\
\n\
'+ var_cores +'\
\n\
'+ vectors +'\
 \n\
  // Creates memory, lock and dfs devices\n\
  tlm_memory mem("mem", 0, MEM_SIZE - 1); // memory\n\
  tlm_lock locker("lock");                // locker\n\
  tlm_intr_ctrl intr_ctrl("intr_ctrl", N_WORKERS);\n\
  //tlm_diretorio dir("dir");\n\
\n\
#ifdef POWER_SIM\n\
  //tlm_dfs dfs("dfs", N_WORKERS, processors); // dfs\n\
#endif\n\
\n\
  '+ procs_interrupt +'\
\n\
  // Processor 0 starts simulatino in ON-mode while the other processors are in\n\
  // OFF-mode\n\
  for (int i = 1; i < N_WORKERS; i++) {\n\
    intr_ctrl.send(i, OFF);// turn off processors 1,..,N_WORKERS-1\n\
  }\n\
  intr_ctrl.send(0, ON); // turn on processor 0 (master)\n\
\n\
  // Creates the NoC with N_WORKERS+2 active nodes\n\
  // The NoC is defined with a bidimensional array, then some inactive nodes\n\
  // will be also\n\
  // created . This NoC has N_WORKERS master nodes (connected with processors)\n\
  // and 3 slave\n\
  // nodes connected with memory, lock and interrrupt controler.\n\
\n\
  // noc constructor parameters:\n\
  // masters = number of processors\n\
  // slaves = 3 (lock, memory and interrupt controler ) or 4 (+ dfs)\n\
  // NumberOfLines and numberOfColumns define the mesh topology\n\
\n\
  int masters = N_WORKERS;\n\
  int slaves = 3; // mem, lock, intr_ctrl\n\
  //int slaves = 4; // mem, lock, intr_ctrl, dir\n\
\n\
#ifdef POWER_SIM\n\
  //slaves++; // dfs\n\
#endif\n\
\n\
  int peripherals = masters + slaves;\n\
  int r = ceil(sqrt(peripherals));\n\
\n\
  tlm_noc noc("noc", N_WORKERS, slaves, r, r);\n\
\n\
  //***************************************************************\n\
  //  Binding platform components\n\
  //*****************************************************************\n\
\n\
  // Connecting memory with the node [0][0] of NoC //\n\
  // noc.mesh[0][0].LOCAL_init_socket.bind(mem.LOCAL_target_socket);\n\
\n\
  int wrMS = 0;\n\
  int emptyMasters = 0;\n\
  int emptySlaves = 0;\n\
  int column = 0, line = 0;\n\
\n\
  // NoC [0][0] -> MEM\n\
  noc.wrapper[wrMS].LOCAL_init_socket.bind(mem.LOCAL_target_socket);\n\
  noc.masterEmptyNodes[emptyMasters].LOCAL_master_init_socket.bind(\
  noc.wrapper[wrMS].LOCAL_target_socket);\n\
  wrMS++;\n\
  emptyMasters++;\n\
  noc.tableOfRouts.newEntry(line, column, MEM_SIZE); // the third argument is the last\n\
                                             // address of the range address of\n\
                                             // LOCK device\n\
\n\
  inc(line,column,r);\n\
\n\
  // NoC [0][1] -> LOCK\n\
  noc.wrapper[wrMS].LOCAL_init_socket.bind(locker.LOCAL_target_socket);\n\
  noc.masterEmptyNodes[emptyMasters].LOCAL_master_init_socket.bind(\
  noc.wrapper[wrMS].LOCAL_target_socket);\n\
  wrMS++;\n\
  emptyMasters++;\n\
  noc.tableOfRouts.newEntry(line, column);\n\
\n\
  inc(line,column,r);\n\
\n\
  /*if (r == 2) {\n\
    line = 1;\n\
    column = 0;\n\
  } else {\n\
    line = 0;\n\
    column = 2;\n\
  }*/\n\
\n\
  // NoC [0][2]-> INTR_CTRL\n\
\n\
  noc.wrapper[wrMS].LOCAL_init_socket.bind(intr_ctrl.LOCAL_target_socket);\n\
  noc.masterEmptyNodes[emptyMasters].LOCAL_master_init_socket.bind(\
  noc.wrapper[wrMS].LOCAL_target_socket);\n\
  wrMS++;\n\
  emptyMasters++;\n\
  noc.tableOfRouts.newEntry(line, column); // the third argument is the last\n\
                                           // address of the range address of\n\
                                           // LOCK device\n\
  inc(line,column,r);\n\
  \n\
  //noc.wrapper[wrMS].LOCAL_init_socket.bind(dir.LOCAL_target_socket);\n\
  //noc.masterEmptyNodes[emptyMasters].LOCAL_master_init_socket.bind(\
  //noc.wrapper[wrMS].LOCAL_target_socket);\n\
  //wrMS++;\n\
  //emptyMasters++;\n\
  //noc.tableOfRouts.newEntry(line, column);\n\
  //inc(line,column,r);\n\
\n\
#ifdef POWER_SIM\n\
  // DFS will be binded with NoC[1][0] in case of NoC 3x3, or NoC[0][4] in other\n\
  // NoCs\n\
  /*noc.wrapper[wrMS].LOCAL_init_socket.bind(dfs.LOCAL_target_socket);\n\
  noc.masterEmptyNodes[emptyMasters].LOCAL_master_init_socket.bind(\
  noc.wrapper[wrMS].LOCAL_target_socket);\n\
  wrMS++;\n\
  emptyMasters++;\n\
  noc.tableOfRouts.newEntry(line, column);\n\
\n\
  inc(line,column,r);*/\n\
\n\
#endif\n\
\n\
  '+ bind_procs +'\
\n\
  while (line < noc.getNumberOfLines()) {\n\
    while (column < noc.getNumberOfColumns()) {\n\
      noc.wrapper[wrMS].LOCAL_init_socket.bind(noc.wrapper[wrMS].LOCAL_target_socket);\n\
      wrMS++;\n\
      //inc (line,column,r);\n\
      column++;\n\
    }\n\
    column = 0;\n\
    line++;\n\
  }\n\
\n\
  noc.preparingRoutingTable();\n\
  //noc.print();\n\
\n\
  // *****************************************************************************************\n\
  // Preparing for Simulation\n\
  // *****************************************************************************************\n\
\n\
  // Preparing the processors arguments\n\
  char **arguments[N_WORKERS];\n\
  for (int i = 0; i < N_WORKERS; i++) {\n\
    arguments[i] = (char **)new char *[ac];\n\
  }\n\
\n\
  for (int i = 0; i < N_WORKERS; i++) {\n\
    for (int j = 0; j < ac; j++) {\n\
      arguments[i][j] = new char[strlen(av[j]) + 1];\n\
      arguments[i][j] = av[j];\n\
    }\n\
  }\n\
\n\
' + load_elfs + '\
\n\
' + init_s + '\
\n\
  // *******************************************************************************************\n\
  // Starting Simulation\n\
  // *******************************************************************************************\n\
\n\
  // Beggining of time measurement\n\
  report_start(av[0], av[1], av[2]);\n\
\n\
  // Beggining of simulation\n\
  sc_start();\n\
\n\
  global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME, "a");\n\
  local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME, "a");\n\
  // ******************************************************************************************\n\
  // Printing Simulation Statistics and Finishing\n\
  // ******************************************************************************************\n\
\n\
' + print_s + '\
\n\
  // Endding the time measurement\n\
  report_end();\n\
\n\
  fclose(global_time_measures);\n\
  fclose(local_time_measures);\n\
\n\
// Printing statistics\n\
#ifdef AC_STATS\n\
' + printing_statistics + '\
#endif\n\
\n\
#ifdef POWER_SIM\n\
  ' + connect_power + '\
#endif\n\
\n\
#ifdef POWER_SIM\n\
  /*global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME, "a");\n\
  local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME, "a");\n\
  double d = 0;\n\
  \n\
  ' + connect_power_info + '\
  printf("\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ", d * 0.000000001);\n\
  fprintf(local_time_measures, "\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ",\
          d * 0.000000001);\n\
  fprintf(global_time_measures, "\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ",\
          d * 0.000000001);\n\
\n\
  fclose(global_time_measures);\n\
  fclose(local_time_measures);*/\n\
#endif\n\
\n\
  // Checking the status\n\
\n\
' + check_status + '\
  noc.destroyComponents();\n\
\n\
  return status;\n\
}\n\
\n\
void report_start(char *platform, char *application, char *cores) {\n\
\n\
  global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME, "a");\n\
  local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME, "a");\n\
\n\
  printf("\\nMPSoCBench: The simulator is prepared.");\n\
  printf("\\nMPSoCBench: Beggining of time simulation measurement.\\n");\n\
  gettimeofday(&startTime, NULL);\n\
  fprintf(local_time_measures, "\\n\\n*******************************************"\
                               "*****************************");\n\
  fprintf(local_time_measures, "\\nPlatform %s with %s cores running %s\\n",\
          platform, cores, application);\n\
\n\
  fprintf(global_time_measures, "\\n\\n******************************************"\
                                "******************************");\n\
  fprintf(global_time_measures, "\\nPlatform %s with %s cores running %s\\n",\
          platform, cores, application);\n\
\n\
  fclose(local_time_measures);\n\
  fclose(global_time_measures);\n\
}\n\
\n\
void report_end() {\n\
\n\
  gettimeofday(&endTime, NULL);\n\
  double tS = startTime.tv_sec * 1000000 + (startTime.tv_usec);\n\
  double tE = endTime.tv_sec * 1000000 + (endTime.tv_usec);\n\
  fprintf(local_time_measures, "\\nTotal Time Taken (seconds):\\t%lf",\
          (tE - tS) / 1000000);\n\
  fprintf(global_time_measures, "\\nTotal Time Taken (seconds):\\t%lf",\
          (tE - tS) / 1000000);\n\
  printf("\\nTotal Time Taken (seconds):\\t%lf", (tE - tS) / 1000000);\n\
\n\
  sc_core::sc_time time = sc_time_stamp();\n\
  fprintf(local_time_measures, "\\nSimulation advance (seconds):\\t%lf",\
          time.to_seconds());\n\
  fprintf(global_time_measures, "\\nSimulation advance (seconds):\\t%lf",\
          time.to_seconds());\n\
  printf("\\nSimulation advance (seconds):\\t%lf", time.to_seconds());\n\
\n\
  printf("\\nMPSoCBench: Ending the time simulation measurement.\\n");\n\
}\n\
\n\
template<class type_core> void load_elf(type_core &proc, tlm_memory &mem, char *filename,\n\
              unsigned int offset, unsigned int memsize) {\n\
\n\
  Elf32_Ehdr ehdr;\n\
  Elf32_Shdr shdr;\n\
  Elf32_Phdr phdr;\n\
  int fd;\n\
  unsigned int i;\n\
  // unsigned int data_mem_size=(0x4FFFFF);\n\
  unsigned int data_mem_size = memsize;\n\
\n\
  if (!filename || ((fd = open(filename, 0)) == -1)) {\n\
    AC_ERROR("Openning application file '" << filename << "': " << strerror(errno) << endl);\n\
    exit(EXIT_FAILURE);\n\
  }\n\
\n\
  // Test if it\'s an ELF file\n\
  if ((read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr)) || // read header\n\
      (strncmp((char *)ehdr.e_ident, ELFMAG, 4) != 0) || // test magic number\n\
      0) {\n\
    close(fd);\n\
    AC_ERROR("File '" << filename << "' is not an elf. : " << strerror(errno)\
                      << endl);\n\
    exit(EXIT_FAILURE);\n\
  }\n\
\n\
  // Set start address\n\
  proc.ac_start_addr = convert_endian(4, ehdr.e_entry, proc.ac_mt_endian);\n\
  if (proc.ac_start_addr > data_mem_size) {\n\
    AC_ERROR("the start address of the application is beyond model memory\\n");\n\
    close(fd);\n\
    exit(EXIT_FAILURE);\n\
  }\n\
\n\
  if (convert_endian(2, ehdr.e_type, proc.ac_mt_endian) == ET_EXEC) {\n\
    // It is an ELF file\n\
    if (first_load)\n\
      AC_SAY("Reading ELF application file: " << filename << endl);\n\
\n\
    for (i = 0; i < convert_endian(2, ehdr.e_phnum, proc.ac_mt_endian); i++) {\n\
      // Get program headers and load segments\n\
      lseek(fd, convert_endian(4, ehdr.e_phoff, proc.ac_mt_endian) +\
                    convert_endian(2, ehdr.e_phentsize, proc.ac_mt_endian) * i,\
            SEEK_SET);\n\
      if (read(fd, &phdr, sizeof(phdr)) != sizeof(phdr)) {\n\
        AC_ERROR("reading ELF program header\\n");\n\
        close(fd);\n\
        exit(EXIT_FAILURE);\n\
      }\n\
\n\
      if (convert_endian(4, phdr.p_type, proc.ac_mt_endian) == PT_LOAD) {\n\
        Elf32_Word j;\n\
        Elf32_Addr p_vaddr = convert_endian(4, phdr.p_vaddr, proc.ac_mt_endian);\n\
        Elf32_Word p_memsz = convert_endian(4, phdr.p_memsz, proc.ac_mt_endian);\n\
        Elf32_Word p_filesz = convert_endian(4, phdr.p_filesz, proc.ac_mt_endian);\n\
        Elf32_Off p_offset = convert_endian(4, phdr.p_offset, proc.ac_mt_endian);\n\
        // Error if segment greater then memory\n\
        if (data_mem_size < p_vaddr + p_memsz) {\n\
          AC_ERROR("not enough memory in ArchC model to load application.\\n");\n\
          close(fd);\n\
          exit(EXIT_FAILURE);\n\
        }\n\
\n\
        // Set heap to the end of the segment\n\
        if (proc.ac_heap_ptr < p_vaddr + p_memsz)\n\
          proc.ac_heap_ptr = p_vaddr + p_memsz;\n\
        if (!proc.dec_cache_size)\n\
          proc.dec_cache_size = proc.ac_heap_ptr;\n\
\n\
        // Load and correct endian\n\
        if (first_load) {\n\
          lseek(fd, p_offset, SEEK_SET);\n\
          for (j = 0; j < p_filesz; j += sizeof(PROCESSOR_NAME_parms::ac_word)) {\n\
            int tmp;\n\
            ssize_t ret_value = read(fd, &tmp, sizeof(PROCESSOR_NAME_parms::ac_word));\n\
            int d = convert_endian(sizeof(PROCESSOR_NAME_parms::ac_word), tmp,\n\
                                   proc.ac_mt_endian);\n\
            mem.write(p_vaddr + j + offset, 4, (unsigned char *)&tmp);\n\
          }\n\
\n\
          int d = 0;\n\
          for (j = p_vaddr + p_filesz; j <= p_memsz - p_filesz; j++)\n\
            mem.write(p_vaddr + j, 4, (unsigned char *)&d);\n\
        } // if\n\
      } // if\n\
    } // for\n\
  } // if\n\
\n\
  close(fd);\n\
}'
		return txt






















































































	def build_platform_het_noc_lt(self):

		i = 1
		defines = '\
\n\
\n/*#ifdef POWER_SIM\
\n  #undef POWER_SIM\
\n  #define POWER_SIM "../../processors/'+self.folder+'/powersc" \
\n#endif*/\
\n\
		'
		var_cores = ''

		vectors = ''

		memports = ' \n  // Initializing Memports \n'

		procs_interrupt = '\
\n    // Binding processors and interruption controller \
\n    int aux = 0;'
		
		load_elfs = '\n\
\n    // Load elf before start\
\n    first_load = true; aux = 0;'
		
		init_s = ''

		print_s = ''

		printing_statistics = ''

		connect_power = ''

		connect_power_info = ''

		check_status = '\
\n    // Checking the status\
\n    bool status;'



		for proc in self.processors:
			defines += '\
\n#include "../../processors/'+ self.folder +'/' + proc["name"] + '.H"\
\n#define PROCESSOR_NAME' + str(i) + ' '+ proc["name"] +' '
			if i == 1:
				defines += '\
\n#define PROCESSOR_NAME_parms '+ proc["name"] +'_parms\
\n\
				'
			else:
				defines += '\
\n#define PROCESSOR_NAME'+str(i)+'_parms '+ proc["name"] +'_parms\
\n\
				'
			var_cores += '\n  int N_CORES_'+str(i)+' = '+ str(self.n_cores[proc["name"]]) +';'

			vectors += '\n\
\n  vector<' + proc["name"] +' *> procs_'+ str(i) +';\
\n\
\n  for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n    char name[10] = "proc";\
\n    char number_str[3];\
\n    sprintf(number_str, "%d", id);\
\n    strcat(name, number_str);\
\n    procs_'+ str(i) +'.push_back(new ' + proc["name"] +'(name, id));\
\n    id++;\
\n  }\
\n\
			'

			memports += '\n\
\n  for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n    procs_'+ str(i) +'[i]->MEM(router.target_export);\
\n    (procs_'+ str(i) +'[i]->MEM_mport).setProcId(procs_'+ str(i) +'[i]->getId());\
\n  }\
\n\
			'

			procs_interrupt +='\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      intr_ctrl.CPU_port[aux](procs_'+ str(i) +'[i]->intr_port);\
\n      aux++;\
\n    }\
\n\
			'
			load_elfs += '\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      load_elf<' + proc["name"] +'>(*procs_'+ str(i) +'[i], mem, arguments[aux][1], 0x000000, MEM_SIZE);\
\n      first_load = false; aux++;\
\n    }\
\n\
			'

			init_s += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->init(); // It passes the arguments to processors\
\n    }\
\n\
			'

			print_s +='\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->PrintStat();\
\n      procs_'+ str(i) +'[i]->FilePrintStat(global_time_measures);\
\n      procs_'+ str(i) +'[i]->FilePrintStat(local_time_measures);\
\n    }\
\n\
			'
			printing_statistics += '\
\n\
\n      for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.time = sc_simulation_time();\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.print();\
\n      }\
\n\
			'

			connect_power +='\n\
\n      /*for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ps.powersc_connect();\
\n        procs_'+ str(i) +'[i]->IC.powersc_connect();\
\n        procs_'+ str(i) +'[i]->DC.powersc_connect();\
\n        }*/\
\n \
			'
			connect_power_info += '\
\n\
\n      for (i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n          d += procs_'+ str(i) +'[i]->ps.getEnergyPerCore();\
\n\
			'

			check_status += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n      status = status + procs_'+ str(i) +'[i]->ac_exit_status;\
\n\
			'


			i += 1

		connect_power += '\
\n      //procs_'+ str(i-1) +'[N_CORES_'+ str(i-1) +' - 1]->ps.report();\n'



		txt = ''
		return txt

	def build_platform_het_noc_lt(self):

		i = 1
		defines = '\
\n\
\n/*#ifdef POWER_SIM\
\n  #undef POWER_SIM\
\n  #define POWER_SIM "../../processors/'+self.folder+'/powersc" \
\n#endif*/\
\n\
		'
		var_cores = ''

		vectors = ''

		procs_interrupt = '\
\n    // Binding processors and interruption controller \
\n    int aux = 0;'

		bind_procs = 'int b = 0;\n '
		
		load_elfs = '\n\
\n    // Load elf before start\
\n    first_load = true; aux = 0;'
		
		init_s = ''

		print_s = ''

		printing_statistics = ''

		connect_power = ''

		connect_power_info = ''

		check_status = '\
\n    // Checking the status\
\n    bool status = 0;'



		for proc in self.processors:
			defines += '\
\n#include "../../processors/'+ self.folder +'/' + proc["name"] + '.H"\
\n#define PROCESSOR_NAME' + str(i) + ' '+ proc["name"] +' '
			if i == 1:
				defines += '\
\n#define PROCESSOR_NAME_parms '+ proc["name"] +'_parms\
\n\
				'
			else:
				defines += '\
\n#define PROCESSOR_NAME'+str(i)+'_parms '+ proc["name"] +'_parms\
\n\
				'
			var_cores += '\n  int N_CORES_'+str(i)+' = '+ str(self.n_cores[proc["name"]]) +';'

			vectors += '\n\
  vector<' + proc["name"] +' *> procs_'+ str(i) +';\n\
\n\
  for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\n\
    char name[10] = "proc";\n\
    char number_str[3];\n\
    sprintf(number_str, "%d", id);\n\
    strcat(name, number_str);\n\
    procs_'+ str(i) +'.push_back(new ' + proc["name"] +'(name, id));\n\
    (procs_'+ str(i) +'[i]->MEM_mport).setProcId(id);\n\
    id++;\n\
  }\n			'


			procs_interrupt +='\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      intr_ctrl.CPU_port[aux](procs_'+ str(i) +'[i]->intr_port);\
\n      aux++;\
\n    }\
\n\
			'

			bind_procs += '\n\
  while(b < procs_'+ str(i) +'.size()){\n\
    procs_'+ str(i) +'[b]->MEM(noc.wrapper[wr].LOCAL_export);\n\
    noc.bindingEmptySlave(wr);\n\
    noc.tableOfRouts.newEntry(line, column);\n\
    wr++; \n\
    inc (line,column,r);\n\
    b++;\n\
  }\n\
  b = 0;\n\
			'

			load_elfs += '\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      load_elf<' + proc["name"] +'>(*procs_'+ str(i) +'[i], mem, arguments[aux][1], 0x000000, MEM_SIZE);\
\n      first_load = false; aux++;\
\n    }\
\n\
			'


			init_s += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->init(); // It passes the arguments to processors\
\n    }\
\n\
			'

			print_s +='\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->PrintStat();\
\n      procs_'+ str(i) +'[i]->FilePrintStat(global_time_measures);\
\n      procs_'+ str(i) +'[i]->FilePrintStat(local_time_measures);\
\n    }\
\n\
			'
			printing_statistics += '\
\n\
\n      for (i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.time = sc_simulation_time();\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.print();\
\n      }\
\n\
			'

			connect_power +='\n\
\n      /*for (i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ps.powersc_connect();\
\n        procs_'+ str(i) +'[i]->IC.powersc_connect();\
\n        procs_'+ str(i) +'[i]->DC.powersc_connect();\
\n        }*/\
\n \
			'
			connect_power_info += '\
\n\
\n      for (i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n          d += procs_'+ str(i) +'[i]->ps.getEnergyPerCore();\
\n\
			'

			check_status += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n      status = status + procs_'+ str(i) +'[i]->ac_exit_status;\
\n\
			'


			i += 1

		connect_power += '\
\n      //procs_'+ str(i-1) +'[N_CORES_'+ str(i-1) +' - 1]->ps.report();\n'
		

		#self.build_defines(defines)



		txt = '\
\n/********************************************************************************\
\n        MPSoCBench Benchmark Suite\
\n        Authors: Liana Duenha\
\n        Supervisor: Rodolfo Azevedo\
\n        Date: July-2012\
\n        www.archc.org/benchs/mpsocbench\
\n\
\n        Computer Systems Laboratory (LSC)\
\n        IC-UNICAMP\
\n        http://www.lsc.ic.unicamp.br/\
\n\
\n\
\n        This source code is part of the MPSoCBench Benchmark Suite, which is a free\
\n        source-code benchmark for evaluation of Electronic Systemc Level designs. \
\n        This benchmark is distributed with hope that it will be useful, but\
\n        without any warranty.\
\n\
\n*********************************************************************************/\
\n\
const char *project_name = "platform.noc.lt";\n\
const char *project_file = "";\n\
const char *archc_version = "";\n\
const char *archc_options = "";\n\
\n\
#include <systemc.h>\n\
#include <sys/time.h>\n\
#include <stdlib.h>\n\
#include <stdio.h>\n\
#include <string.h>\n\
#include "../../defines.h"\n\
\n\
#include "tlm_memory.h"\n\
#include "tlm_lock.h"\n\
#include "tlm_dfs.h"\n\
#include "tlm_noc.h"\n\
#include "tlm_intr_ctrl.h"\n\
//#include "tlm_diretorio.h"\n\
\n\
using user::tlm_memory;\n\
using user::tlm_noc;\n\
using user::tlm_lock;\n\
using user::tlm_intr_ctrl;\n\
//using user::tlm_diretorio;\n\
\n\
#ifdef POWER_SIM\n\
using user::tlm_dfs;\n\
#endif\n\
\n\
'+ defines +'\
\n\
/* This is an arbitrary limit for the number of processors\n\
 If necessary, this value can be modified, but\n\
 there is no guarantee that all parallel applications will work properly */\n\
\n\
// Global variables\n\
int N_WORKERS;\n\
struct timeval startTime;\n\
struct timeval endTime;\n\
FILE *local_time_measures;\n\
FILE *global_time_measures;\n\
\n\
bool first_load;\n\
// Functions\n\
void report_start(char *, char *, char *);\n\
void report_end();\n\
template<class type_core> void load_elf(type_core &, tlm_memory &, char *, unsigned int, unsigned int);\n\
\n\
int inc (int &line, int &column, int &r)\n\
{\n\
  column = (column+1)%r;\n\
  if (column == 0) line++;  \n\
}\n\
\n\
int sc_main(int ac, char *av[]) {\n\
\n\
  sc_report_handler::set_actions("/IEEE_Std_1666/deprecated", SC_DO_NOTHING);\n\
\n\
  int N_WORKERS;\n\
\n\
  if (ac != 0) {\n\
    N_WORKERS = atoi(av[2]);\n\
    if (N_WORKERS > MAX_WORKERS) {\n\
      printf("\\nThe amount of processors must be less than 64 %d.\\n", MAX_WORKERS);\n\
      exit(1);\n\
    }\n\
\n\
  } else {\n\
    printf("\\nNo arguments for main.\\n");\n\
    exit(1);\n\
  }\n\
\n\
  ///************************************************************************************\n\
  // Creating platform components\n\
  //	- A memory with MEM_SIZE bytes\n\
  //	- A lock device\n\
  //	- A set of N_WORKERS processors\n\
  //	- A NoC with suficient nodes useful to communicate memory, lock and\n\
  //processors\n\
  //*************************************************************************************\n\
\n\
  // Creates a set of processors\n\
\n\
  int id = 0;\n\
\n\
' + var_cores + '\
\n\
' + vectors + '\
\n\
  // Creates memory, lock and dfs devices\n\
  tlm_memory mem("mem", 0, MEM_SIZE - 1); // memory\n\
  tlm_lock locker("lock");                // locker\n\
  tlm_intr_ctrl intr_ctrl("intr_ctrl", N_WORKERS);\n\
  //tlm_diretorio dir("dir");\n\
\n\
#ifdef POWER_SIM\n\
  //tlm_dfs dfs("dfs", N_WORKERS, processors); // dfs\n\
#endif\n\
\n\
' + procs_interrupt + '\
\n\
  // Creates the NoC with N_WORKERS+2 active nodes\n\
  // The NoC is defined with a bidimensional array, then some inactive nodes\n\
  // will be also\n\
  // created . This NoC has N_WORKERS master nodes (connected with processors)\n\
  // and 2 slave\n\
  // nodes connected with memory and lock devices.\n\
\n\
  // noc constructor parameters:\n\
  // masters = number of processors\n\
  // slaves = 2 (lock, memory) or 3 (+ dfs)\n\
  // NumberOfLines and numberOfColumns define the mesh topology\n\
\n\
  int masters = N_WORKERS;\n\
  int slaves = 3; // mem, lock , intr_ctrl\n\
  //int slaves = 4; // mem, lock , intr_ctrl, diretório\n\
\n\
#ifdef POWER_SIM\n\
  //slaves++; // dfs\n\
#endif\n\
\n\
  int peripherals = masters + slaves;\n\
  int r = ceil(sqrt(peripherals));\n\
\n\
  tlm_noc noc("noc", N_WORKERS, slaves, r, r);\n\
\n\
  //***************************************************************\n\
  //  Binding platform components\n\
  //*****************************************************************\n\
\n\
  int wr = 0;\n\
  int line = 0;\n\
  int column = 0;\n\
\n\
  noc.wrapper[wr].LOCAL_port(mem.target_export);\n\
  noc.tableOfRouts.newEntry(line, column, MEM_SIZE);\n\
  wr++;\n\
\n\
  inc(line,column,r);\n\
\n\
  noc.wrapper[wr].LOCAL_port(locker.target_export);\n\
  noc.tableOfRouts.newEntry(line, column);\n\
  wr++;\n\
\n\
  inc(line,column,r);\n\
\n\
  // Connecting the interrupt controler (intr_ctrl) with the noc node [1][0]\n\
  // (noc 2x2) or [0][2] (other cases)\n\
  // third peripheral address space: 0x21000000...0x22000000-1\n\
  noc.wrapper[wr].LOCAL_port(intr_ctrl.target_export);\n\
  noc.tableOfRouts.newEntry(line, column);\n\
  wr++;\n\
  inc (line,column,r);\n\
\n\
  //noc.wrapper[wr].LOCAL_port(dir.target_export);\n\
  //noc.tableOfRouts.newEntry(line, column);\n\
  //wr++;\n\
  //inc (line,column,r);\n\
\n\
#ifdef POWER_SIM\n\
  /*noc.wrapper[wr].LOCAL_port(dfs.target_export);\n\
  wr++;\n\
  noc.tableOfRouts.newEntry(line, column);\n\
  inc (line,column,r);*/\n\
 \n\
#endif\n\
\n\
'+ bind_procs +'\
\n\
  while (line < noc.getNumberOfLines()) {\n\
    while (column < noc.getNumberOfColumns()) {\n\
      noc.bindingEmptySlave(wr); // bind mesh to the slave\n\
      wr++;\n\
      column++;\n\
    }\n\
    column = 0;\n\
    line++;\n\
  }\n\
\n\
  noc.preparingRoutingTable();\n\
  noc.print();\n\
  for (int i = 1; i < N_WORKERS; i++) {\n\
    intr_ctrl.send(i, OFF); // turn off processors 0,..,N_WORKERS-1\n\
  }\n\
\n\
  intr_ctrl.send(0, ON); // turn on processor 0 (master)\n\
\n\
  // *****************************************************************************************\n\
  // Preparing for Simulation\n\
  // *****************************************************************************************\n\
\n\
  // Preparing the processors arguments\n\
  char **arguments[N_WORKERS];\n\
  for (int i = 0; i < N_WORKERS; i++) {\n\
    arguments[i] = (char **)new char *[ac];\n\
  }\n\
\n\
  for (int i = 0; i < N_WORKERS; i++) {\n\
    for (int j = 0; j < ac; j++) {\n\
      arguments[i][j] = new char[strlen(av[j]) + 1];\n\
      arguments[i][j] = av[j];\n\
      // printf ("%s\\n",arguments[i][j]);\n\
    }\n\
  }\n\
\n\
  // Load elf before start\n\
\n\
'+ load_elfs +'\
\n\
'+ init_s +'\
\n\
  // *******************************************************************************************\n\
  // Starting Simulation\n\
  // *******************************************************************************************\n\
\n\
  // Beggining of time measurement\n\
\n\
  report_start(av[0], av[1], av[2]);\n\
\n\
  // Beggining of simulation\n\
\n\
  sc_start();\n\
\n\
  // ******************************************************************************************\n\
  // Printing Simulation Statistics and Finishing\n\
  // ******************************************************************************************\n\
\n\
'+ print_s +'\
\n\
  // Endding the time measurement\n\
  report_end();\n\
  cerr << endl;\n\
\n\
// Printing statistics\n\
#ifdef AC_STATS\n\
'+ printing_statistics +'\
#endif\n\
\n\
#ifdef POWER_SIM\n\
'+ connect_power +'\
#endif\n\
\n\
#ifdef POWER_SIM\n\
  /*double d = 0;\n\
  '+ connect_power_info +'\
  printf("\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ", d * 0.000000001);\n\
  fprintf(local_time_measures, "\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ", d * 0.000000001);\n\
  fprintf(global_time_measures, "\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ", d * 0.000000001);*/\n\
#endif\n\
\n\
'+ check_status +'\
\n\
  fclose(local_time_measures);\n\
  fclose(global_time_measures);\n\
\n\
  return status;\n\
}\n\
\n\
void report_start(char *platform, char *application, char *cores) {\n\
\n\
  global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME, "a");\n\
  local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME, "a");\n\
\n\
  printf("\\nMPSoCBench: The simulator is prepared.");\n\
  printf("\\nMPSoCBench: Beggining of time simulation measurement.\\n");\n\
  gettimeofday(&startTime, NULL);\n\
  fprintf(local_time_measures, "\\n\\n*******************************************"\n\
                               "*****************************");\n\
  fprintf(local_time_measures, "\\nPlatform %s with %s cores running %s\\n", platform, cores, application);\n\
  fprintf(global_time_measures, "\\n\\n************************************************************************");\n\
  fprintf(global_time_measures, "\\nPlatform %s with %s cores running %s\\n", platform, cores, application);\n\
}\n\
\n\
void report_end() {\n\
  // global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME,"a");\n\
  // local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME,"a");\n\
\n\
  gettimeofday(&endTime, NULL);\n\
  double tS = startTime.tv_sec * 1000000 + (startTime.tv_usec);\n\
  double tE = endTime.tv_sec * 1000000 + (endTime.tv_usec);\n\
  fprintf(local_time_measures, "\\nTotal Time Taken (seconds):\\t%lf", (tE - tS) / 1000000);\n\
  fprintf(global_time_measures, "\\nTotal Time Taken (seconds):\\t%lf", (tE - tS) / 1000000);\n\
  printf("\\nTotal Time Taken (seconds):\\t%lf", (tE - tS) / 1000000);\n\
\n\
  sc_core::sc_time time = sc_time_stamp();\n\
  fprintf(local_time_measures, "\\nSimulation advance (seconds):\\t%lf", time.to_seconds());\n\
  fprintf(global_time_measures, "\\nSimulation advance (seconds):\\t%lf", time.to_seconds());\n\
  printf("\\nSimulation advance (seconds):\\t%lf", time.to_seconds());\n\
\n\
  printf("\\nMPSoCBench: Ending the time simulation measurement.\\n");\n\
}\n\
\n\
template<class type_core> void load_elf(type_core &proc, tlm_memory &mem, char *filename, unsigned int offset, unsigned int memsize) {\n\
\n\
  Elf32_Ehdr ehdr;\n\
  Elf32_Shdr shdr;\n\
  Elf32_Phdr phdr;\n\
  int fd;\n\
  unsigned int i;\n\
\n\
  unsigned int data_mem_size = memsize;\n\
\n\
  if (!filename || ((fd = open(filename, 0)) == -1)) {\n\
    AC_ERROR("Openning application file '" << filename << "': " << strerror(errno) << endl);\n\
    exit(EXIT_FAILURE);\n\
  }\n\
\n\
  // Test if it\'s an ELF file\n\
  if ((read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr)) || // read header\n\
      (strncmp((char *)ehdr.e_ident, ELFMAG, 4) != 0) || // test magic number\n\
      0) {\
    close(fd);\n\
    AC_ERROR("File '" << filename << "' is not an elf. : " << strerror(errno) << endl);\n\
    exit(EXIT_FAILURE);\n\
  }\n\
\n\
  // Set start address\n\
  proc.ac_start_addr = convert_endian(4, ehdr.e_entry, proc.ac_mt_endian);\n\
  if (proc.ac_start_addr > data_mem_size) {\n\
    AC_ERROR("the start address of the application is beyond model memory\\n");\n\
    close(fd);\n\
    exit(EXIT_FAILURE);\n\
  }\n\
\n\
  if (convert_endian(2, ehdr.e_type, proc.ac_mt_endian) == ET_EXEC) {\n\
    // It is an ELF file\n\
    if (first_load)\n\
      AC_SAY("Reading ELF application file: " << filename << endl);\n\
\n\
    for (i = 0; i < convert_endian(2, ehdr.e_phnum, proc.ac_mt_endian); i++) {\n\
      // Get program headers and load segments\n\
      lseek(fd, convert_endian(4, ehdr.e_phoff, proc.ac_mt_endian) +\
                    convert_endian(2, ehdr.e_phentsize, proc.ac_mt_endian) * i,\
            SEEK_SET);\n\
      if (read(fd, &phdr, sizeof(phdr)) != sizeof(phdr)) {\n\
        AC_ERROR("reading ELF program header\\n");\n\
        close(fd);\n\
        exit(EXIT_FAILURE);\n\
      }\n\
\n\
      if (convert_endian(4, phdr.p_type, proc.ac_mt_endian) == PT_LOAD) {\n\
        Elf32_Word j;\n\
        Elf32_Addr p_vaddr = convert_endian(4, phdr.p_vaddr, proc.ac_mt_endian);\n\
        Elf32_Word p_memsz = convert_endian(4, phdr.p_memsz, proc.ac_mt_endian);\n\
        Elf32_Word p_filesz = convert_endian(4, phdr.p_filesz, proc.ac_mt_endian);\n\
        Elf32_Off p_offset = convert_endian(4, phdr.p_offset, proc.ac_mt_endian);\n\
        // Error if segment greater then memory\n\
        if (data_mem_size < p_vaddr + p_memsz) {\n\
          AC_ERROR("not enough memory in ArchC model to load application.\\n");\n\
          close(fd);\n\
          exit(EXIT_FAILURE);\n\
        }\n\
\n\
        // Set heap to the end of the segment\n\
        if (proc.ac_heap_ptr < p_vaddr + p_memsz)\n\
          proc.ac_heap_ptr = p_vaddr + p_memsz;\n\
        if (!proc.dec_cache_size)\n\
          proc.dec_cache_size = proc.ac_heap_ptr;\n\
\n\
        // Load and correct endian\n\
        if (first_load) {\n\
          lseek(fd, p_offset, SEEK_SET);\n\
          for (j = 0; j < p_filesz;\n\
               j += sizeof(PROCESSOR_NAME_parms::ac_word)) {\n\
            int tmp;\n\
            ssize_t ret_value = read(fd, &tmp, sizeof(PROCESSOR_NAME_parms::ac_word));\n\
            int d = convert_endian(sizeof(PROCESSOR_NAME_parms::ac_word), tmp, proc.ac_mt_endian);\n\
            mem.direct_write(&tmp, p_vaddr + j + offset);\n\
          }\n\
\n\
          int d = 0;\n\
          for (j = p_vaddr + p_filesz; j <= p_memsz - p_filesz; j++)\n\
            mem.direct_write(&d, p_vaddr + j);\n\
        } // if\n\
      } // if\n\
    } // for\n\
  } // if\n\
\n\
  close(fd);\n\
}		'
		return txt






















































































	def build_platform_het_router_lt(self):

		i = 1

		defines = '\
\n\
\n#ifdef POWER_SIM\
\n  #undef POWER_SIM\
\n  #define POWER_SIM "../../processors/'+self.folder+'/powersc" \
\n#endif\
\n\
		'
		var_cores = ''

		vectors = ''

		memports = ' \n  // Initializing Memports \n'

		procs_interrupt = '\
\n    // Binding processors and interruption controller \
\n    int aux = 0;'
		
		load_elfs = '\n\
\n    // Load elf before start\
\n    first_load = true; aux = 0;'
		
		init_s = ''

		print_s = ''

		printing_statistics = ''

		connect_power = ''

		connect_power_info = ''

		check_status = '\
\n    // Checking the status\
\n    bool status;'



		for proc in self.processors:
			defines += '\
\n#include "../../processors/'+ self.folder +'/' + proc["name"] + '.H"\
\n//#define PROCESSOR_NAME' + str(i) + ' ' + proc["name"] + ' '
			if i == 1:
				defines += '\
\n#define PROCESSOR_NAME ' + proc["name"] + '\
\n#define PROCESSOR_NAME_parms '+ proc["name"] +'_parms\
\n\
				'
			else:
				defines += '\
\n#define PROCESSOR_NAME' + str(i) + ' ' + proc["name"] + '\
\n#define PROCESSOR_NAME'+ str(i)+'_parms '+ proc["name"] +'_parms\
\n\
				'
			var_cores += '\n  int N_CORES_'+str(i)+' = '+ str(self.n_cores[proc["name"]]) +';'

			vectors += '\n\
\n  vector<' + proc["name"] +' *> procs_'+ str(i) +';\
\n\
\n  for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n    char name[10] = "proc";\
\n    char number_str[3];\
\n    sprintf(number_str, "%d", id);\
\n    strcat(name, number_str);\
\n    procs_'+ str(i) +'.push_back(new ' + proc["name"] +'(name, id));\
\n    id++;\
\n  }\
\n\
			'

			memports += '\n\
\n  for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n    procs_'+ str(i) +'[i]->MEM(router.target_export);\
\n    (procs_'+ str(i) +'[i]->MEM_mport).setProcId(procs_'+ str(i) +'[i]->getId());\
\n  }\
\n\
			'

			procs_interrupt +='\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      intr_ctrl.CPU_port[aux](procs_'+ str(i) +'[i]->intr_port);\
\n      aux++;\
\n    }\
\n\
			'
			load_elfs += '\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      load_elf<' + proc["name"] +'>(*procs_'+ str(i) +'[i], mem, arguments[aux][1], 0x000000, MEM_SIZE);\
\n      first_load = false; aux++;\
\n    }\
\n\
			'

			init_s += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->init(); // It passes the arguments to processors\
\n    }\
\n\
			'

			print_s +='\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n      procs_'+ str(i) +'[i]->PrintStat();\
\n      procs_'+ str(i) +'[i]->FilePrintStat(global_time_measures);\
\n      procs_'+ str(i) +'[i]->FilePrintStat(local_time_measures);\
\n    }\
\n\
			'
			printing_statistics += '\
\n\
\n      for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.time = sc_simulation_time();\
\n        procs_'+ str(i) +'[i]->ac_sim_stats.print();\
\n      }\
\n\
			'

			
			connect_power +='\n\
\n      for (int i = 0; i < N_CORES_'+ str(i) +'; i++) {\
\n        procs_'+ str(i) +'[i]->ps.powersc_connect();\
\n        procs_'+ str(i) +'[i]->IC.powersc_connect();\
\n        //procs_'+ str(i) +'[i]->DC.powersc_connect();\
\n      }\
\n		//procs_'+ str(i) +'[N_CORES_'+ str(i) +' - 1]->ps.report();\
\n \
			'

			connect_power_info += '\
\n\
\n      for (int i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n          d += procs_'+ str(i) +'[i]->ps.getEnergyPerCore();\
\n\
			'

			check_status += '\
\n\
\n    for (int i = 0; i < N_CORES_'+ str(i) +'; i++)\
\n      status = status + procs_'+ str(i) +'[i]->ac_exit_status;\
\n\
			'


			i += 1

		if self.power:
			connect_power += '\
\n      //procs_'+ str(i-1) +'[N_CORES_'+ str(i-1) +' - 1]->ps.report();\n'
		else:
			connect_power += '\
\n      procs_'+ str(i-1) +'[N_CORES_'+ str(i-1) +' - 1]->ps.report();\n'


		
		self.build_defines(defines)


		txt = '\
\n/********************************************************************************\
\n    MPSoCBench Benchmark Suite \
\n    Authors: Liana Duenha \
\n    Supervisor: Rodolfo Azevedo \
\n    Date: July-2012 \
\n    www.archc.org/benchs/mpsocbench \
\n\
\n    Computer Systems Laboratory (LSC) \
\n    IC-UNICAMP \
\n    http://www.lsc.ic.unicamp.br/ \
\n\
\n\
\n    This source code is part of the MPSoCBench Benchmark Suite, which is a free \
\n    source-code benchmark for evaluation of Electronic Systemc Level designs.\
\n    This benchmark is distributed with hope that it will be useful, but\
\n    without any warranty.\
\n\
\n*********************************************************************************/\
\n \
\nconst char *project_name = "platform.router.het.lt"; \
\nconst char *project_file = "";\
\nconst char *archc_version = ""; \
\nconst char *archc_options = "";\
\n\
\n#include <systemc.h>\
\n#include <sys/time.h>\
\n#include <stdlib.h>\
\n#include <stdio.h>\
\n#include <string.h>\
\n#include "../../defines.h"\
\n\
\n#include "tlm_memory.h"\
\n#include "tlm_router.h"\
\n#include "tlm_lock.h"\
\n//#include "tlm_dfs.h"\
\n#include "tlm_intr_ctrl.h"\
\n//#include "tlm_diretorio.h"\
\n\
\n\
\nusing user::tlm_memory;\
\nusing user::tlm_router;\
\nusing user::tlm_lock;\
\nusing user::tlm_intr_ctrl;\
\n//using user::tlm_diretorio;\
\n\
\n#ifdef POWER_SIM\
\n//using user::tlm_dfs;\
\n#endif\
\n\
\n// Global variables\
\nint N_WORKERS;\
\nstruct timeval startTime;\
\nstruct timeval endTime;\
\n\
\nFILE *global_time_measures;\
\nFILE *local_time_measures;\
\n\
\nbool first_load;\
\n// Functions\
\nvoid report_start(char *, char *, char *);\
\nvoid report_end();\
\n\
\ntemplate<class type_core> void load_elf(type_core &, tlm_memory &, char *, unsigned int, unsigned int);\
\n\
\nint sc_main (int ac, char *av[]){\
\n\
\n  sc_report_handler::set_actions("/IEEE_Std_1666/deprecated", SC_DO_NOTHING);\
\n  // Checking the arguments\
\n  if (ac != 0) {\
\n    N_WORKERS = atoi(av[2]);\
\n\
\n    if (N_WORKERS > MAX_WORKERS) {\
\n      printf("\\nThe amount of processors must be less than 64 %d.\\n", MAX_WORKERS);\
\n      exit(1);\
\n    }\
\n  }\
\n  else {\
\n    printf("\\nNo arguments for main.\\n");\
\n    exit(1);\
\n  }\
\n\
\n  int id = 0;\
\n\
'+ var_cores +'\
'+ vectors +'\
\n\
\n  // Platform components \
\n  tlm_memory mem("mem", 0, MEM_SIZE - 1); // memory\
\n  tlm_router router("router");            // router\
\n  tlm_lock locker("locker");              // locker\
\n  tlm_intr_ctrl intr_ctrl("intr_ctrl", N_WORKERS);\
\n  //tlm_diretorio dir("dir");\
\n  #ifdef POWER_SIM\
\n    //tlm_dfs dfs("dfs", N_CORES_1, &procs_1); // dfs\
\n  #endif\
\n\
\n  // Binding ports\
\n  router.MEM_port(mem.target_export);\
\n  router.LOCK_port(locker.target_export);\
\n  router.INTR_CTRL_port(intr_ctrl.target_export);\
\n  //router.DIR_port(dir.target_export);\
\n\
\n  #ifdef POWER_SIM\
\n    //router.DFS_port(dfs.target_export);\
\n  #endif\
\n\
'+ memports +'\
'+ procs_interrupt + '\
\n\
\n   // Processor 0 starts simulatino in ON-mode while the other processors are in\
\n    // OFF-mode\
\n    for (int i = 1; i < N_WORKERS; i++) {\
\n      intr_ctrl.send(i, OFF);\
\n    }\
\n    intr_ctrl.send(0, ON); // turn on processor 0 (master)\
\n\
\n    // Preparing the arguments\
\n    char **arguments[N_WORKERS];\
\n    for (int i = 0; i < N_WORKERS; i++) {\
\n      arguments[i] = (char **)new char *[ac];\
\n    }\
\n\
\n    for (int i = 0; i < N_WORKERS; i++) {\
\n      for (int j = 0; j < ac; j++) {\
\n        arguments[i][j] = new char[strlen(av[j]) + 1];\
\n        arguments[i][j] = av[j];\
\n      }\
\n    }\
\n\
'+ load_elfs + '\
'+ init_s +' \
\n    report_start(av[0], av[1], av[2]);\
\n    // Beggining of simulation\
\n\
\n    sc_start();\
	  '+ print_s +'\
\n    // Printing statistics\
\n    #ifdef AC_STATS\
		'+ printing_statistics +'\
\n    #endif\
\n\
\n    #ifdef POWER_SIM\n\
		'+connect_power+'\
\n    #endif\
\n\
\n    #ifdef POWER_SIM\
\n      /*double d = 0;\
\n\
\n      // Connect Power Information from ArchC with PowerSC\
		'+connect_power_info+'\
\n\
\n      printf("\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ", d * 0.000000001);\
\n      fprintf(local_time_measures, "\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ", d * 0.000000001);\
\n      fprintf(global_time_measures, "\\n\\nTOTAL ENERGY (ALL CORES): %.10f J\\n\\n ",d * 0.000000001);*/\
\n    #endif\
\n\
'+ check_status +'\
\n    fclose(local_time_measures);\
\n    fclose(global_time_measures);\
\n\
\n    return status;\
\n}\
\n\
\nvoid report_start(char *platform, char *application, char *cores) {\
\n\
\n  global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME, "a");\
\n  local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME, "a");\
\n\
\n  printf("\\nMPSoCBench: The simulator is prepared.");\
\n  printf("\\nMPSoCBench: Beggining of time simulation measurement.\\n");\
\n  gettimeofday(&startTime, NULL);\
\n  fprintf(local_time_measures, "\\n\\n*******************************************"\
\n                               "*****************************");\
\n  fprintf(local_time_measures, "\\nPlatform %s with %s cores running %s\\n",\
\n          platform, cores, application);\
\n\
\n  fprintf(global_time_measures, "\\n\\n******************************************"\
\n                                "******************************");\
\n  fprintf(global_time_measures, "\\nPlatform %s with %s cores running %s\\n",\
\n          platform, cores, application);\
\n\
\n  //fclose(local_time_measures);\
\n  //fclose(global_time_measures);\
\n}\
\n\
\nvoid report_end() {\
\n  // global_time_measures = fopen(GLOBAL_FILE_MEASURES_NAME,"a");\
\n  // local_time_measures = fopen(LOCAL_FILE_MEASURES_NAME,"a");\
\n\
\n  gettimeofday(&endTime, NULL);\
\n  double tS = startTime.tv_sec * 1000000 + (startTime.tv_usec);\
\n  double tE = endTime.tv_sec * 1000000 + (endTime.tv_usec);\
\n  fprintf(local_time_measures, "\\nTotal Time Taken (seconds):\\t%lf",\
\n          (tE - tS) / 1000000);\
\n  fprintf(global_time_measures, "\\nTotal Time Taken (seconds):\\t%lf",\
\n          (tE - tS) / 1000000);\
\n  printf("\\nTotal Time Taken (seconds):\\t%lf", (tE - tS) / 1000000);\
\n\
\n  sc_core::sc_time time = sc_time_stamp();\
\n  fprintf(local_time_measures, "\\nSimulation advance (seconds):\\t%lf",\
\n          time.to_seconds());\
\n  fprintf(global_time_measures, "\\nSimulation advance (seconds):\\t%lf",\
\n          time.to_seconds());\
\n  printf("\\nSimulation advance (seconds):\\t%lf", time.to_seconds());\
\n\
\n  printf("\\nMPSoCBench: Ending the time simulation measurement.\\n");\
\n}\
\n\
\ntemplate<class type_core> void load_elf(type_core &proc, tlm_memory &mem, char *filename,\
\n              unsigned int offset, unsigned int memsize) {\
\n\
\n  Elf32_Ehdr ehdr;\
\n  Elf32_Shdr shdr;\
\n  Elf32_Phdr phdr;\
\n  int fd;\
\n  unsigned int i;\
\n  // unsigned int data_mem_size=(0x4FFFFF);\
\n  unsigned int data_mem_size = memsize;\
\n\
\n  if (!filename || ((fd = open(filename, 0)) == -1)) {\n\
    AC_ERROR("Openning application file '" << filename\
                                           << "': " << strerror(errno) << endl);\
\n    exit(EXIT_FAILURE);\
\n  }\
\n\
\n  // Test if its an ELF file\
\n  if ((read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr)) || // read header\
\n      (strncmp((char *)ehdr.e_ident, ELFMAG, 4) != 0) || // test magic number\
\n      0) {\
\n    close(fd);\
\n    AC_ERROR("File \'" << filename << "\' is not an elf. : " << strerror(errno)\
\n                      << endl);\
\n    exit(EXIT_FAILURE);\
\n  }\
\n\
\n  // Set start address\
\n\
\n  proc.ac_start_addr = convert_endian(4, ehdr.e_entry, proc.ac_mt_endian);\
\n\
\n  if (proc.ac_start_addr > data_mem_size) {\
\n    printf("ac_start_addr: %d   data_mem_size: %d", proc.ac_start_addr,\
\n           data_mem_size);\
\n    AC_ERROR("the start address of the application is beyond model memory\\n");\
\n    close(fd);\
\n    exit(EXIT_FAILURE);\
\n  }\
\n\
\n  if (convert_endian(2, ehdr.e_type, proc.ac_mt_endian) == ET_EXEC) {\
\n    // It is an ELF file\
\n    if (first_load)\
\n      AC_SAY("Reading ELF application file: " << filename << endl);\
\n\
\n    for (i = 0; i < convert_endian(2, ehdr.e_phnum, proc.ac_mt_endian); i++) {\
\n      // Get program headers and load segments\
\n      lseek(fd, convert_endian(4, ehdr.e_phoff, proc.ac_mt_endian) +\
\n                    convert_endian(2, ehdr.e_phentsize, proc.ac_mt_endian) * i,\
\n            SEEK_SET);\
\n      if (read(fd, &phdr, sizeof(phdr)) != sizeof(phdr)) {\
\n        AC_ERROR("reading ELF program header\\n");\
\n        close(fd);\
\n        exit(EXIT_FAILURE);\
\n      }\
\n\
\n      if (convert_endian(4, phdr.p_type, proc.ac_mt_endian) == PT_LOAD) {\
\n        Elf32_Word j;\
\n        Elf32_Addr p_vaddr = convert_endian(4, phdr.p_vaddr, proc.ac_mt_endian);\
\n        Elf32_Word p_memsz = convert_endian(4, phdr.p_memsz, proc.ac_mt_endian);\
\n        Elf32_Word p_filesz =\
\n            convert_endian(4, phdr.p_filesz, proc.ac_mt_endian);\
\n        Elf32_Off p_offset =\
\n            convert_endian(4, phdr.p_offset, proc.ac_mt_endian);\
\n\
\n        //printf("data_mem_size: %d  application size: %d", data_mem_size, p_vaddr+p_memsz);\
\n        // Error if segment greater then memory\
\n        if (data_mem_size < p_vaddr + p_memsz) {\
\n          printf("data_mem_size: %d  application size: %d", data_mem_size,\
\n                 p_vaddr + p_memsz);\
\n          AC_ERROR("not enough memory in ArchC model to load application.\\n");\
\n          close(fd);\
\n          exit(EXIT_FAILURE);\
\n        }\
\n\
\n        // printf("ac_heap_ptr: %d", proc.ac_heap_ptr);\
\n        // Set heap to the end of the segment\
\n        if (proc.ac_heap_ptr < p_vaddr + p_memsz)\
\n          proc.ac_heap_ptr = p_vaddr + p_memsz;\
\n        if (!proc.dec_cache_size)\
\n          proc.dec_cache_size = proc.ac_heap_ptr;\
\n\
\n        // Load and correct endian\
\n\
\n        /**************************************************************** \
\n        Como vai funcionar apenar parar o primeiro carregamento podemos\
\n        definir o primeiro PROCESSOR_NAME_parms do primeiro PROCESSOR da\
\n        lista.\
\n        ******************************************************************/\
\n        if (first_load) {\
\n          lseek(fd, p_offset, SEEK_SET);\
\n          for (j = 0; j < p_filesz;\
\n               j += sizeof(PROCESSOR_NAME_parms::ac_word)) {\
\n            int tmp;\
\n            ssize_t ret_value =\
\n                read(fd, &tmp, sizeof(PROCESSOR_NAME_parms::ac_word));\
\n            int d = convert_endian(sizeof(PROCESSOR_NAME_parms::ac_word), tmp,\
\n                                   proc.ac_mt_endian);\
\n            mem.direct_write(&tmp, p_vaddr + j + offset);\
\n          }\
\n\
\n          int d = 0;\
\n          for (j = p_vaddr + p_filesz; j <= p_memsz - p_filesz; j++)\
\n            mem.direct_write(&d, p_vaddr + j);\
\n        } // if\
\n\
\n      } // if\
\n\
\n    } // for\
\n  } // if\
\n\
\n  close(fd);\
\n }'
		return txt