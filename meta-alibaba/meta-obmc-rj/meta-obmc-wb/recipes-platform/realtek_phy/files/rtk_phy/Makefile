include Rules.mk

CUR_SOURCE=${wildcard *.c}
OBJ = ${patsubst %.c, %.o, $(CUR_SOURCE)}

LIB += $(BUILD_CFALGS) $(BUILD_LDFLAGS) -lpthread

APP = rtk_phy
BUILD_DIR = ./build
ELF_FILE = $(BUILD_DIR)/$(APP)
MAP_FILE = $(BUILD_DIR)/$(APP).map.sym
INCLUDE = -Iinclude

.PHONY: build
build:make-dir $(addprefix $(BUILD_DIR)/,$(OBJ))
	$(CC) -o $(ELF_FILE) $(addprefix $(BUILD_DIR)/,$(OBJ)) $(LINKFLAGS) $(LIB)


# 创建build目录用来存放.o文件
.PHONY: make-dir
make-dir:
	@mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o:%.c make-dir
	$(CC) -c $(CFLAGS) $(INCLUDE) $< -o $@

.PHONY: install
install:

	cp -p $(ELF_FILE) $(install_sbin_dir)

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)


