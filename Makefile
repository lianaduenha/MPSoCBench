#FILE GENERATED AUTOMAGICALLY - DO NOT EDIT
export SHELL := /bin/bash
export PROCESSOR_BASE := mips
export PROCESSOR := mips300 mips800
export NUMPROCESSORS := 2
export SOFTWARE := dijkstra
export PLATFORM := platform.router.het.lt
export CROSS := mips-newlib-elf-gcc
export POWER_SIM_FLAG := 
export ACSIM_FLAGS := -abi -ndc 
export WAIT_TRANSPORT_FLAG := 
export TRANSPORT := block
export MEM_SIZE_DEFAULT := -DMEM_SIZE=536870912
export RUNDIRNAME := mips.router.het.lt.4.dijkstra
export ENDIANESS := -DAC_GUEST_BIG_ENDIAN
ifeq ($(PROCESSOR_BASE),arm)
export CFLAGS_AUX := -DPROCARM
endif
ifeq ($(PROCESSOR_BASE),mips)
export CFLAGS_AUX := -DPROCMIPS
endif
ifeq ($(PROCESSOR_BASE),sparc)
export CFLAGS_AUX := -DPROCSPARC
endif
ifeq ($(PROCESSOR_BASE),powerpc)
export CFLAGS_AUX := -DPROCPOWERPC
endif
include Makefile.rules
