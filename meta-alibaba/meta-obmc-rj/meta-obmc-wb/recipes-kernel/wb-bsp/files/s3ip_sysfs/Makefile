SRC		= $(shell pwd)

export S3IP_DIR_PATH = $(SRC)

obj-y += device_driver/
obj-y += switch_driver/
obj-y += sysfs_driver/

ccflags-y += -I$(KERNEL_EXTRA_HEADER_PATH)

all:
	$(MAKE) -C $(KERNEL_SRC) M=$(SRC)

modules_install:
	$(MAKE) -C $(KERNEL_SRC) M=$(SRC) modules_install

clean:
	rm -f *.o *~ core .depend .*.cmd *.ko *.mod.c
	rm -f Module.markers Module.symvers modules.order
	rm -rf .tmp_versions Modules.symvers
