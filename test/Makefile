# test/Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# valores por defecto
SIM ?= icarus
FST ?= -fst # Usar el formato FST, mas eficiente
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src

# Selecciona que se simula (make -B MODULE=xxx):
#   project        -> chip Tiny Tapeout completo (decoder_alu + alu_top)  [por defecto]
#   arithmetic     -> unidad aritmetica sola
#   logic          -> unidad logica sola
#   barrel_shifter -> unidad desplazadora sola
#   alu_top        -> ALU combinacional completa (sin decodificador serie)
#   decoder_alu    -> decodificador serie + ALU
MODULE ?= project

ifeq ($(MODULE),project)
    PROJECT_SOURCES      = project.v decoder_alu.v alu_top.v arithmetic.v logic.v barrel_shifter.v
    TOPLEVEL             = tb
    COCOTB_TEST_MODULES  = test
else ifeq ($(MODULE),arithmetic)
    PROJECT_SOURCES      = arithmetic.v
    TOPLEVEL             = arithmetic
    COCOTB_TEST_MODULES  = test_arithmetic
else ifeq ($(MODULE),logic)
    PROJECT_SOURCES      = logic.v
    TOPLEVEL             = Logico_8bits
    COCOTB_TEST_MODULES  = test_logic
else ifeq ($(MODULE),barrel_shifter)
    PROJECT_SOURCES      = barrel_shifter.v
    TOPLEVEL             = barrel_shifter
    COCOTB_TEST_MODULES  = test_barrel_shifter
else ifeq ($(MODULE),alu_top)
    PROJECT_SOURCES      = alu_top.v arithmetic.v logic.v barrel_shifter.v
    TOPLEVEL             = alu_top
    COCOTB_TEST_MODULES  = test_alu_top
else ifeq ($(MODULE),decoder_alu)
    PROJECT_SOURCES      = decoder_alu.v alu_top.v arithmetic.v logic.v barrel_shifter.v
    TOPLEVEL             = decoder_alu
    COCOTB_TEST_MODULES  = test_decoder_alu
endif

ifneq ($(GATES),yes)

# Simulacion RTL:
SIM_BUILD               = sim_build/rtl_$(MODULE)
VERILOG_SOURCES         += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

else

# Simulacion a nivel de compuertas (solo valida para MODULE=project):
SIM_BUILD               = sim_build/gl
COMPILE_ARGS             += -DGL_TEST
COMPILE_ARGS             += -DFUNCTIONAL
COMPILE_ARGS             += -DSIM
VERILOG_SOURCES          += $(PDK_ROOT)/ihp-sg13g2/libs.ref/sg13g2_io/verilog/sg13g2_io.v
VERILOG_SOURCES          += $(PDK_ROOT)/ihp-sg13g2/libs.ref/sg13g2_stdcell/verilog/sg13g2_stdcell.v

# esto se copia mediante el workflow de la accion GDS
VERILOG_SOURCES          += $(PWD)/gate_level_netlist.v

endif

# Permite compartir configuracion entre el diseno y el testbench via `include`:
COMPILE_ARGS             += -I$(SRC_DIR)

# Solo el testbench del proyecto completo usa el wrapper tb.v
ifeq ($(MODULE),project)
    VERILOG_SOURCES += $(PWD)/tb.v
endif

# incluye las reglas make de cocotb, que se encargan de configurar el simulador
include $(shell cocotb-config --makefiles)/Makefile.sim
