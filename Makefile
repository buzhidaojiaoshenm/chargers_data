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
	@bash -c "source venv/bin/activate && PYTHONPATH=. python src/main.py"

# 清理数据
clean-data:
	@echo "清理数据文件..."
	@rm -f data/*
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