.PHONY: tuner clean

tuner:
	pip uninstall -y enum34
	pyinstaller --onefile tuner.spec

clean:
	rm -rf build
	rm -f dist/tuner
	rm -f dist/options.json
	rm -f dist/results.*
	rm -rf dist/configs
	rm -rf tuner/configs
	rm -f tuner/options.json
	rm -f tuner/results.xlsx
	rm -f tuner/results.csv
