BUILD := uv run --script tools/build.py

.PHONY: build check stl clean

build:
	$(BUILD) $(MODEL)

check:
	$(BUILD) --check $(MODEL)

stl:
	$(BUILD) --format stl $(MODEL)

clean:
	rm -rf out
