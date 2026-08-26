.PHONY: install dev server run clean

install:
	pip install -r requirements.txt

dev:
	uvicorn web.app:app --reload

server:
	uvicorn web.app:app --host 0.0.0.0 --port 8080

run:
	python main.py "帮我测试 example.com"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
