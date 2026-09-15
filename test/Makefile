# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src

# Aquí declaramos todos los módulos de tu ALU
PROJECT_SOURCES = project.v alu_top.v arithmetic.v barrel_shifter.v decoder_alu.v logic.v

ifneq ($(GATES),yes)
# RTL simulation:
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS += -I $(SRC_DIR)
else
# Gate level simulation:
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v
# Banderas críticas para simular las celdas estándar de IHP
COMPILE_ARGS += -DGL_TEST
COMPILE_ARGS += -DFUNCTIONAL
COMPILE_ARGS += -DUSE_POWER_PINS
COMPILE_ARGS += -DSIM
COMPILE_ARGS += -DUNIT_DELAY=\#1
endif

# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb

# MODULE is the basename of the Python test file (test.py)
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
