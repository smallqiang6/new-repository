include Rules.mk

OBJ = scan-asdsmc.o

# lib_sbin_dir = ../../dfd-lib/1.0-r1

LIB += $(BUILD_CFALGS) $(BUILD_LDFLAGS) -lpthread

APP = scan-asdsmc
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


