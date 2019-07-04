PKGNAME     = salson
APP_PATH    = $(PKGNAME)/$(PKGNAME).py

test:
	pylint --disable=anomalous-backslash-in-string \
           --disable=missing-docstring \
        $(APP_PATH)
	python $(APP_PATH) sample/i2c.csv output_i2c.json
