#

platform_common-objs := platform_common_module.o dfd_tlveeprom.o
obj-m	+= wb_platform_i2c_dev.o
obj-m	+= wb_i2c_dev.o
obj-m	+= wb_platform.o
obj-m	+= wb_i2c_mux_pca9641.o
obj-m	+= wb_i2c_mux_pca954x.o
obj-m	+= aspeed_peci.o
obj-m	+= aspeed_adc_hwmon.o
obj-m	+= wb_eeprom_93xx46.o
obj-m	+= wb_mac_bsc.o
obj-m	+= wb_ina3221.o
obj-m	+= wb_isl68137.o
obj-m	+= wb_tps53622.o
obj-m	+= wb_fpga_i2c_bus_drv.o
obj-m	+= wb_fpga_pca954x_drv.o
obj-m	+= wb_spi_93xx46.o
obj-m	+= wb_wdt.o
obj-m	+= hw_test.o
obj-m	+= wb_pmbus_core.o
obj-m	+= wb_ucd9000.o
obj-m	+= wb_tmp401.o
obj-m	+= wb_spi_nor_device.o
obj-m	+= platform_common.o
obj-m	+= wb_lm75.o
obj-m	+= wb_xdpe12284.o
obj-m	+= wb_xdpe132g5c_pmbus.o
obj-m	+= wb_csu550.o
obj-m	+= wb_spi_dev.o
obj-m	+= wb_indirect_dev.o
obj-m	+= wb_xdpe132g5c.o
obj-m	+= wb_ucd9081.o
obj-m	+= wb_aspeed_adc.o
obj-m	+= wb_aspeed_common.o
obj-m	+= wb_spi_gpio_device.o
obj-m 	+= wb_dev_resume.o
obj-m 	+= wb_rc32312.o

ccflags-y += -I$(KERNEL_EXTRA_HEADER_PATH)

SRC := $(shell pwd)

all:
	$(MAKE) -C $(KERNEL_SRC) M=$(SRC)

modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(SRC) modules_install

clean:
	rm -f *.o *~ core .depend .*.cmd *.ko *.mod.c
	rm -f Module.markers Module.symvers modules.order
	rm -rf .tmp_versions Modules.symvers
