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

# ---------------------------------------------------------------------------
# Simulacion RTL  (make -B)
# ---------------------------------------------------------------------------
SIM_BUILD = sim_build/rtl

VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))
COMPILE_ARGS += -I $(SRC_DIR)

else

# ---------------------------------------------------------------------------
# Simulacion a nivel de compuertas  (make -B GATES=yes)
# ---------------------------------------------------------------------------
SIM_BUILD = sim_build/gl

# Defines que usan el netlist post-layout y los modelos del PDK.
COMPILE_ARGS += -DGL_TEST
COMPILE_ARGS += -DFUNCTIONAL
COMPILE_ARGS += -DSIM

# Raiz del PDK. La accion de Tiny Tapeout la exporta como /home/runner/pdk.
PDK_ROOT ?= /home/runner/pdk

# OJO: la carpeta del PDK se llama "ihp-sg13g2", no "sg13g2".
PDK_SG13G2_ROOT = $(PDK_ROOT)/ihp-sg13g2

# Modelos de celdas. Estos dos archivos contienen TODAS las celdas que
# aparecen en el netlist (logica, flip-flops, buffers de retardo, tie,
# fill y decap). No usar `find` sobre el PDK: arrastra vistas duplicadas
# y rompe la elaboracion.
VERILOG_SOURCES += $(PDK_SG13G2_ROOT)/libs.ref/sg13g2_io/verilog/sg13g2_io.v
VERILOG_SOURCES += $(PDK_SG13G2_ROOT)/libs.ref/sg13g2_stdcell/verilog/sg13g2_stdcell.v

# Netlist de compuertas: lo copia aqui el job gl_test de la accion GDS.
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Testbench
VERILOG_SOURCES += $(PWD)/tb.v

TOPLEVEL = tb
MODULE = test

include $(shell cocotb-config --makefiles)/Makefile.sim
