PY=python3

all:

proto:
	$(PY) -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --proto_path=. ./reporting.proto

server:
	$(PY) server.py


venv:
	$(info $(PY) -m venv myenv)
	$(info source myenv/bin/activate)
	$(info pip3 install --no-cache-dir -r requirements.txt)

clean:
	rm -rf __pycache__
	rm -rf *pb2*.py


.PHONY: all clean