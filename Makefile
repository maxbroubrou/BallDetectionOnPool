PYTHON=python3

all: generate

generate:
	python3 images_generator.py

draw:
	python3 DrawBoundingBox.py