# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = project.v alu_top.v arithmetic.v barrel_shifter.v decoder_alu.v logic.v

ifneq ($(GATES),yes)
# RTL simulation:
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS += -I $(SRC_DIR)
else
# Gate level simulation for IHP (sg13g2)
# Se incluye el netlist sintetizado y los modelos primitivos del PDK que exige Icarus
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v
# Si el entorno de Tiny Tapeout IHP expone las celdas primitivas del PDK, las enlazamos:
ifdef PDK_ROOT
VERILOG_SOURCES += $(PDK_ROOT)/sg13g2/libs.ref/sg13g2_ivt/verilog/sg13g2_ivt.v
endif
endif

# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb

# MODULE is the basename of the Python test file (test.py)
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
