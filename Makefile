.PHONY: init test run clean clean-data clean-all

SHELL := /bin/bash  # 指定使用 bash 作为 shell

# 默认目标
all: init

# 初始化项目
init:
	@echo "初始化项目..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

# 运行测试
test:
	@echo "运行测试..."
	@if [ ! -d "venv" ]; then \
		echo "错误：请先运行 'make init' 初始化项目"; \
		exit 1; \
	fi
	@bash -c "source venv/bin/activate && python -m pytest tests/"

# 运行项目
run:
	@echo "运行项目..."
	@if [ ! -d "venv" ]; then \
		echo "错误：请先运行 'make init' 初始化项目"; \
		exit 1; \
	fi
	@bash -c "source venv/bin/activate && PYTHONPATH=. python src/main.py $(ARGS)"

# 运行简化测试（默认只处理一个组的一个任务）
run-simple:
	@echo "运行简化测试（只处理一个组的第一个任务）..."
	@if [ ! -d "venv" ]; then \
		echo "错误：请先运行 'make init' 初始化项目"; \
		exit 1; \
	fi
	@bash -c "source venv/bin/activate && PYTHONPATH=. python src/main.py -g shanghai_polygon --task-count 1 $(ARGS)"

# 运行API测试
test-api:
	@echo "运行API连接测试..."
	@if [ ! -d "venv" ]; then \
		echo "错误：请先运行 'make init' 初始化项目"; \
		exit 1; \
	fi
	@bash -c "source venv/bin/activate && python src/examples/api_test.py"

# 清理数据和日志
clean-data:
	@echo "清理数据文件..."
	@rm -rf data/*
	@rm -rf logs/*
	@touch data/.gitkeep
	@echo "数据清理完成"

# 清理项目（不包括数据）
clean:
	@echo "清理项目..."
	@rm -rf venv
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

# 清理所有（包括数据）
clean-all: clean clean-data
	@echo "项目完全清理完成" 