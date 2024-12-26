obj-y	+= common/
obj-y	+= firmware_driver/
obj-y	+= s3ip_sysfs/

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