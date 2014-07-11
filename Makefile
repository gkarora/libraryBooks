CONTENTS := web_server.py server.py

CONTENTS_EXEC := activate

CONTENTS_WEB := datachart.html style.css util.js

CONFIGURATION := configuration/service-id.json

ARCHIVE := archive.tar.bz2

BUILD = build

.PHONY = all dist clean install

all: dist

dist: install $(ARCHIVE)

install: $(CONTENTS) $(CONTENTS_EXEC) $(CONFIGURATION) $(CONTENTS_WEB)
	rm -rf $(BUILD)/
	install -m 755 -d $(BUILD)
	install -m 755 -d $(BUILD)/pub
	install -m 755 -d $(BUILD)/configuration
	install -m 644 $(CONTENTS)            $(BUILD)/
	install -m 755 $(CONTENTS_EXEC)       $(BUILD)/
	install -m 644 $(CONTENTS_WEB)        $(BUILD)/pub
	install -m 644 $(CONFIGURATION)       $(BUILD)/configuration

$(ARCHIVE): $(BUILD)
	rm -f $@
	tar -cjvf $@ -C $(BUILD) .

clean:
	rm -r $(ARCHIVE) $(BUILD)
