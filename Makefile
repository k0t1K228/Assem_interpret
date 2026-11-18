PY = PYTHONPATH=src python

.PHONY: test demo

test:
	$(PY) -m unittest discover -s tests -t . -v

demo:
	$(PY) -m uvm.asm_cli examples/spec_tests.csv out/spec.bin --test
	$(PY) -m uvm.asm_cli examples/vector_abs.csv out/vector_abs.bin
	$(PY) -m uvm.interp_cli out/vector_abs.bin out/vector_abs.dump.csv 10 27
	cat out/vector_abs.dump.csv
