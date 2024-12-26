include Rules.mk

BUILD_DIR = build
SRCS=$(wildcard *.c)
OBJS=$(patsubst %.c, $(BUILD_DIR)/%.o, $(SRCS))
LIB += $(BUILD_CFALGS) $(BUILD_LDFLAGS) -lpthread 

APP = firmware_upgrade
ELF_FILE = $(BUILD_DIR)/$(APP)
INCLUDE = -Iinclude

.PHONY: build
build: $(OBJS)
	$(CC) -o $(ELF_FILE) $(OBJS) $(LINKFLAGS) $(LIB)

$(OBJS):$(SRCS)
	@if [ ! -d ${BUILD_DIR} ]; then mkdir -p ${BUILD_DIR} ;fi
	$(CC) -c $(CFLAGS) $(INCLUDE) $(*F).c -o $@

.PHONY: install
install:
	echo "firmware_upgrade install success."

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
