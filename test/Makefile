# Makefile

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(PWD)/../src

PROJECT_SOURCES = \
	project.v \
	alu_top.v \
	arithmetic.v \
	barrel_shifter.v \
	decoder_alu.v \
	logic.v

ifneq ($(GATES),yes)

# RTL simulation
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS += -I $(SRC_DIR)

else

# Gate-level simulation
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

# Locate the IHP SG13G2 PDK models
PDK_ROOT ?= /home/runner/pdk

PDK_SG13G2_ROOT = $(PDK_ROOT)/sg13g2

# Include every Verilog model found inside the SG13G2 PDK.
# This includes standard cells, IO cells, fillers, decaps,
# antenna cells and other physical cells.
PDK_VERILOG_FILES := $(shell find $(PDK_SG13G2_ROOT) \
	-type f \
	-name "*.v" \
	-print)

VERILOG_SOURCES += $(PDK_VERILOG_FILES)

endif

# Testbench
VERILOG_SOURCES += $(PWD)/tb.v

TOPLEVEL = tb
MODULE = test

include $(shell cocotb-config --makefiles)/Makefile.sim