#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# CZ Career Architect - Test Runner Script
# ═══════════════════════════════════════════════════════════════
#
# Этот скрипт автоматизирует запуск тестов для проекта.
# Использование:
#   ./run_tests.sh           - Запустить все тесты
#   ./run_tests.sh coverage  - Запустить с покрытием кода
#   ./run_tests.sh quick     - Быстрый запуск без verbose
#   ./run_tests.sh file <name> - Запустить конкретный файл
#
# ═══════════════════════════════════════════════════════════════

set -e  # Выйти при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}  CZ Career Architect - Test Runner${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Проверка текущей директории
check_directory() {
    print_info "Проверка директории..."
    
    if [ ! -d "tests" ] || [ ! -d "base_for_agent_cv" ]; then
        print_error "Ошибка: Запустите скрипт из корня проекта!"
        echo ""
        echo "Текущая директория: $(pwd)"
        echo ""
        echo "Правильно:"
        echo "  cd /path/to/cz-career-architect"
        echo "  ./run_tests.sh"
        echo ""
        exit 1
    fi
    
    print_success "Директория: $(pwd)"
}

# Проверка Python
check_python() {
    print_info "Проверка Python..."
    
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        print_error "Python не найден! Установите Python 3.9+"
        exit 1
    fi
    
    # Определить команду python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Python установлен: $PYTHON_VERSION"
}

# Проверка виртуального окружения
check_venv() {
    if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        print_warning "Обнаружено виртуальное окружение, но оно не активировано"
        print_info "Активация виртуального окружения..."
        
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            print_success "Виртуальное окружение активировано"
        elif [ -f "venv/Scripts/activate" ]; then
            source venv/Scripts/activate
            print_success "Виртуальное окружение активировано"
        fi
    elif [ -n "$VIRTUAL_ENV" ]; then
        print_success "Виртуальное окружение активно: $VIRTUAL_ENV"
    fi
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."
    
    if ! $PYTHON_CMD -c "import pytest" 2>/dev/null; then
        print_error "pytest не установлен!"
        echo ""
        read -p "Установить зависимости сейчас? (y/n) " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Установка зависимостей..."
            $PYTHON_CMD -m pip install -r requirements.txt
            print_success "Зависимости установлены"
        else
            print_error "Невозможно продолжить без pytest"
            echo "Установите зависимости вручную:"
            echo "  pip install -r requirements.txt"
            exit 1
        fi
    else
        print_success "Зависимости установлены"
    fi
}

# Проверка переменных окружения
check_environment() {
    print_info "Проверка переменных окружения..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY не установлен"
        print_info "Некоторые тесты могут использовать заглушки"
        
        if [ -f ".env" ]; then
            print_info "Найден файл .env - загрузка переменных..."
            export $(cat .env | grep -v '^#' | xargs)
            
            if [ -n "$OPENAI_API_KEY" ]; then
                print_success "OPENAI_API_KEY загружен из .env"
            fi
        else
            print_info "Совет: Создайте файл .env с OPENAI_API_KEY"
        fi
    else
        print_success "OPENAI_API_KEY установлен"
    fi
}

# Запуск тестов
run_tests() {
    local mode=$1
    local test_arg=$2
    
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}Запуск тестов...${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""
    
    case $mode in
        "coverage")
            print_info "Режим: Тесты с покрытием кода"
            $PYTHON_CMD -m pytest tests/ \
                --cov=base_for_agent_cv \
                --cov-report=term-missing \
                --cov-report=html \
                -v
            
            echo ""
            print_success "HTML отчет создан: htmlcov/index.html"
            ;;
            
        "quick")
            print_info "Режим: Быстрый запуск"
            $PYTHON_CMD -m pytest tests/ -q
            ;;
            
        "file")
            if [ -z "$test_arg" ]; then
                print_error "Укажите имя файла теста"
                echo "Пример: ./run_tests.sh file test_config"
                exit 1
            fi
            
            print_info "Режим: Запуск файла tests/${test_arg}.py"
            
            if [ -f "tests/${test_arg}.py" ]; then
                $PYTHON_CMD -m pytest "tests/${test_arg}.py" -v
            elif [ -f "tests/${test_arg}" ]; then
                $PYTHON_CMD -m pytest "tests/${test_arg}" -v
            else
                print_error "Файл не найден: tests/${test_arg}.py"
                exit 1
            fi
            ;;
            
        *)
            print_info "Режим: Все тесты"
            $PYTHON_CMD -m pytest tests/ -v
            ;;
    esac
    
    local exit_code=$?
    
    echo ""
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    
    if [ $exit_code -eq 0 ]; then
        print_success "Тесты успешно завершены!"
    else
        print_error "Тесты завершились с ошибками"
        exit $exit_code
    fi
    
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

# Главная функция
main() {
    print_header
    
    # Показать текущую директорию
    echo -e "📂 Текущая директория: ${GREEN}$(pwd)${NC}"
    echo ""
    
    # Проверки
    check_directory
    check_python
    check_venv
    check_dependencies
    check_environment
    
    # Запуск тестов
    local mode=${1:-"default"}
    local test_arg=$2
    
    run_tests "$mode" "$test_arg"
}

# Обработка параметров командной строки
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "CZ Career Architect - Test Runner"
    echo ""
    echo "Использование:"
    echo "  ./run_tests.sh              Запустить все тесты"
    echo "  ./run_tests.sh coverage     Запустить с покрытием кода"
    echo "  ./run_tests.sh quick        Быстрый запуск без verbose"
    echo "  ./run_tests.sh file <name>  Запустить конкретный файл"
    echo ""
    echo "Примеры:"
    echo "  ./run_tests.sh"
    echo "  ./run_tests.sh coverage"
    echo "  ./run_tests.sh file test_config"
    echo ""
    echo "Требования:"
    echo "  - Python 3.9+"
    echo "  - pip install -r requirements.txt"
    echo "  - Запуск из корня проекта"
    echo ""
    exit 0
fi

# Запуск
main "$@"
