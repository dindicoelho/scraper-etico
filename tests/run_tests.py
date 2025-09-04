#!/usr/bin/env python3
"""
Script para executar todos os testes do ScraperEtico

Este script executa todos os testes unitários e gera um relatório de cobertura.
"""

import unittest
import sys
import os
from pathlib import Path

# Adicionar diretório src ao path
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def run_all_tests():
    """Executa todos os testes unitários"""
    
    # Descobrir e executar todos os testes
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    # Configurar runner com verbosidade
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=True)
    
    print("=" * 70)
    print("🧪 EXECUTANDO TESTES DO SCRAPER ÉTICO")
    print("=" * 70)
    
    # Executar testes
    result = runner.run(suite)
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    successful = total_tests - failures - errors - skipped
    
    print(f"✅ Testes executados: {total_tests}")
    print(f"🎉 Sucessos: {successful}")
    print(f"❌ Falhas: {failures}")  
    print(f"💥 Erros: {errors}")
    print(f"⏭️  Pulados: {skipped}")
    
    success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    # Mostrar detalhes das falhas
    if result.failures:
        print("\n" + "🔍 DETALHES DAS FALHAS:")
        print("-" * 50)
        for test, traceback in result.failures:
            print(f"❌ {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
    
    # Mostrar detalhes dos erros
    if result.errors:
        print("\n" + "💥 DETALHES DOS ERROS:")
        print("-" * 50) 
        for test, traceback in result.errors:
            print(f"💥 {test}")
            error_lines = traceback.split('\n')
            # Pegar última linha não vazia com a descrição do erro
            for line in reversed(error_lines):
                if line.strip():
                    print(f"   {line.strip()}")
                    break
    
    print("=" * 70)
    
    # Retornar código de saída
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_module):
    """Executa testes de um módulo específico"""
    
    print(f"🧪 Executando testes de {test_module}")
    
    # Importar e executar módulo específico
    try:
        if test_module == 'scraper':
            from test_scraper_etico import TestScraperEtico
            suite = unittest.TestLoader().loadTestsFromTestCase(TestScraperEtico)
        elif test_module == 'analyzer':
            from test_analyzer import TestRobotsAnalyzer
            suite = unittest.TestLoader().loadTestsFromTestCase(TestRobotsAnalyzer)
        elif test_module == 'batch':
            from test_batch_processor import TestBatchProcessor
            suite = unittest.TestLoader().loadTestsFromTestCase(TestBatchProcessor)
        else:
            print(f"❌ Módulo '{test_module}' não encontrado")
            return 1
            
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulo de teste: {e}")
        return 1


def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas"""
    
    required_modules = ['requests', 'pandas']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Dependências não encontradas:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n📦 Instale com: pip install " + " ".join(missing_modules))
        return False
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Executar testes do ScraperEtico')
    parser.add_argument(
        '--module', 
        choices=['scraper', 'analyzer', 'batch'],
        help='Executar testes de um módulo específico'
    )
    parser.add_argument(
        '--check-deps', 
        action='store_true',
        help='Verificar dependências antes de executar'
    )
    
    args = parser.parse_args()
    
    # Verificar dependências se solicitado
    if args.check_deps:
        if not check_dependencies():
            sys.exit(1)
        print("✅ Todas as dependências estão instaladas\n")
    
    # Executar testes
    if args.module:
        exit_code = run_specific_test(args.module)
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)