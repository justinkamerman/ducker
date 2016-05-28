SRC = application.py requirements.txt static templates


.PHONY: clean

ducker.zip: $(SRC)
	zip -r $@ $^

clean:
	rm -rf *.zip

