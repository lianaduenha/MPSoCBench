#FILE GENERATED AUTOMAGICALLY - DO NOT EDIT
export SHELL := /bin/bash
export PROCESSOR_BASE := mips
export PROCESSOR := mips300 mips800
export NUMPROCESSORS := 4
export SOFTWARE := dijkstra
export PLATFORM := platform.noc.het.at
export CROSS := mips-newlib-elf-gcc
export POWER_SIM_FLAG := 
export ACSIM_FLAGS := -abi -ndc 
export WAIT_TRANSPORT_FLAG := 
export TRANSPORT := nonblock
export MEM_SIZE_DEFAULT := -DMEM_SIZE=536870912
export RUNDIRNAME := mips.noc.het.at.4.dijkstra
export ENDIANESS := -DAC_GUEST_BIG_ENDIAN


include Makefile.rules
