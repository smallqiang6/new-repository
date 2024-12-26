include Rules.mk

OBJ = cpu-peci-space.o 
LIB += $(BUILD_CFALGS) $(BUILD_LDFLAGS) -lpthread 

APP = cpu-peci-space
BUILD_DIR = build
ELF_FILE = $(BUILD_DIR)/$(APP)
MAP_FILE = $(BUILD_DIR)/$(APP).map.sym
INCLUDE = -Iinclude


.PHONY: build
build:make-dir $(addprefix $(BUILD_DIR)/,$(OBJ))
	$(CC) -o $(ELF_FILE) $(addprefix $(BUILD_DIR)/,$(OBJ)) $(LINKFLAGS) $(LIB)

.PHONY: make-dir
make-dir:
	@mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o:%.c make-dir
	$(CC) -c $(CFLAGS) $(INCLUDE) $< -o $@

.PHONY: install
install:
	echo "cpu error gpio monitor install success."

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR)
