
# Makefile
# Cocotb simulation for TinyTapeout IHP SG13G2

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

# RTL / Gate-level simulation
ifneq ($(GATES),yes)

VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS += -I $(SRC_DIR)

else

# Gate-level simulation for IHP SG13G2
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

# Include IHP PDK Verilog models only when they exist.
# Do not hard-code a required sg13g2_ivt.v path.

ifdef PDK_ROOT

PDK_SG13G2 = $(PDK_ROOT)/sg13g2

# Standard-cell Verilog models
VERILOG_SOURCES += $(wildcard $(PDK_SG13G2)/libs.ref/sg13g2_stdcell/verilog/*.v)

# I/O cell Verilog models
VERILOG_SOURCES += $(wildcard $(PDK_SG13G2)/libs.ref/sg13g2_io/verilog/*.v)

# IVT models, if provided by this PDK installation
VERILOG_SOURCES += $(wildcard $(PDK_SG13G2)/libs.ref/sg13g2_ivt/verilog/*.v)

endif

endif

# Testbench
VERILOG_SOURCES += $(PWD)/tb.v

TOPLEVEL = tb
MODULE = test

# Cocotb
include $(shell cocotb-config --makefiles)/Makefile.sim
