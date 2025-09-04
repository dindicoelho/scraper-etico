#!/usr/bin/env python3
"""
ANÁLISE DE RESULTADOS - Para entender seus dados de scraping
"""

import json
import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

def analisar_csv(arquivo_csv):
    """Analisar resultados de um arquivo CSV"""
    print(f"📊 ANALISANDO: {arquivo_csv}")
    print("-" * 50)
    
    with open(arquivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        dados = list(reader)
    
    print(f"📋 Total de registros: {len(dados)}")
    
    # Análise de sucessos
    sucessos = [d for d in dados if d.get('success') == 'True']
    falhas = [d for d in dados if d.get('success') == 'False']
    
    print(f"✅ Sucessos: {len(sucessos)} ({len(sucessos)/len(dados)*100:.1f}%)")
    print(f"❌ Falhas: {len(falhas)} ({len(falhas)/len(dados)*100:.1f}%)")
    
    # Análise por domínio
    dominios = Counter(d.get('domain', 'N/A') for d in dados)
    print(f"\n🌐 TOP 5 DOMÍNIOS:")
    for dominio, count in dominios.most_common(5):
        print(f"   {dominio}: {count} URLs")
    
    # Análise de status codes
    status_codes = Counter(d.get('status_code', 'N/A') for d in sucessos)
    print(f"\n📊 STATUS CODES:")
    for status, count in status_codes.most_common(5):
        print(f"   {status}: {count} vezes")
    
    # Análise de erros
    if falhas:
        erros = Counter(d.get('error_type', 'N/A') for d in falhas)
        print(f"\n❌ TIPOS DE ERRO:")
        for erro, count in erros.most_common(3):
            print(f"   {erro}: {count} vezes")
    
    # Sites que bloquearam
    bloqueados = [d for d in dados if d.get('robots_allowed') == 'False']
    if bloqueados:
        print(f"\n🚫 SITES QUE BLOQUEARAM:")
        for site in bloqueados[:5]:
            print(f"   {site.get('url', 'N/A')[:50]}...")
    
    return dados

def analisar_json(arquivo_json):
    """Analisar resultados de um arquivo JSON"""
    print(f"📊 ANALISANDO: {arquivo_json}")
    print("-" * 50)
    
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Metadata do job
    if 'job_metadata' in dados:
        meta = dados['job_metadata']
        print(f"🆔 Job ID: {meta.get('job_id', 'N/A')}")
        print(f"📈 Taxa de sucesso: {meta.get('success_count', 0)}/{meta.get('total_urls', 0)}")
        
        if 'duration' in meta and meta['duration']:
            print(f"⏱️  Tempo total: {meta['duration'].get('human_readable', 'N/A')}")
    
    # Análise dos resultados
    if 'results' in dados:
        resultados = dados['results']
        print(f"\n📋 Total de resultados: {len(resultados)}")
        
        # Tamanho médio das respostas
        tamanhos = [r.get('response_size', 0) for r in resultados if r.get('response_size')]
        if tamanhos:
            tamanho_medio = sum(tamanhos) / len(tamanhos)
            print(f"📏 Tamanho médio das páginas: {tamanho_medio:.0f} bytes")
        
        # Tempo médio de resposta
        tempos = [r.get('response_time', 0) for r in resultados if r.get('response_time')]
        if tempos:
            tempo_medio = sum(tempos) / len(tempos)
            print(f"⏱️  Tempo médio de resposta: {tempo_medio:.2f}s")
    
    return dados

def gerar_relatorio_completo(pasta_dados="dados_producao"):
    """Gerar relatório completo de todos os arquivos"""
    print("📋 RELATÓRIO COMPLETO DE SCRAPING")
    print("=" * 60)
    
    pasta = Path(pasta_dados)
    if not pasta.exists():
        print(f"❌ Pasta {pasta_dados} não encontrada!")
        return
    
    # Encontrar arquivos
    csvs = list(pasta.glob("*.csv"))
    jsons = list(pasta.glob("*.json"))
    
    print(f"📁 Pasta analisada: {pasta}")
    print(f"📄 Arquivos CSV: {len(csvs)}")
    print(f"📄 Arquivos JSON: {len(jsons)}")
    
    if not csvs and not jsons:
        print("⚠️ Nenhum arquivo de dados encontrado!")
        return
    
    # Analisar arquivo mais recente
    if csvs:
        csv_recente = max(csvs, key=lambda x: x.stat().st_mtime)
        print(f"\n🔍 ANALISANDO ARQUIVO MAIS RECENTE:")
        dados_csv = analisar_csv(csv_recente)
    
    if jsons:
        json_recente = max(jsons, key=lambda x: x.stat().st_mtime)
        print(f"\n🔍 ANÁLISE DETALHADA (JSON):")
        dados_json = analisar_json(json_recente)
    
    # Histórico de execuções
    print(f"\n📈 HISTÓRICO DE EXECUÇÕES:")
    todos_arquivos = sorted(csvs + jsons, key=lambda x: x.stat().st_mtime, reverse=True)
    
    for i, arquivo in enumerate(todos_arquivos[:10]):  # Últimos 10
        modificado = datetime.fromtimestamp(arquivo.stat().st_mtime)
        tamanho = arquivo.stat().st_size
        print(f"   {i+1:2d}. {arquivo.name} ({tamanho} bytes) - {modificado.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n💡 COMO VER DADOS:")
    print(f"   open {pasta}/")
    print(f"   head -10 {csv_recente.name if csvs else 'arquivo.csv'}")
    print(f"   cat {json_recente.name if jsons else 'arquivo.json'} | python3 -m json.tool")

if __name__ == "__main__":
    print("🎯 ANALISADOR DE RESULTADOS DE SCRAPING")
    print("=" * 50)
    
    # Menu de opções
    print("📋 OPÇÕES:")
    print("1. Analisar pasta dados_producao/")
    print("2. Analisar pasta resultados_personalizados/")
    print("3. Analisar arquivo específico")
    print("4. Relatório completo")
    
    opcao = input("\n🤔 Escolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        gerar_relatorio_completo("dados_producao")
    
    elif opcao == "2":
        gerar_relatorio_completo("resultados_personalizados")
    
    elif opcao == "3":
        arquivo = input("📄 Digite o caminho do arquivo: ").strip()
        arquivo_path = Path(arquivo)
        if arquivo_path.exists():
            if arquivo.endswith('.csv'):
                analisar_csv(arquivo_path)
            elif arquivo.endswith('.json'):
                analisar_json(arquivo_path)
            else:
                print("❌ Formato não suportado. Use CSV ou JSON.")
        else:
            print(f"❌ Arquivo não encontrado: {arquivo}")
    
    elif opcao == "4":
        print("📊 RELATÓRIOS COMPLETOS:")
        gerar_relatorio_completo("dados_producao")
        print("\n" + "="*60)
        gerar_relatorio_completo("resultados_personalizados")
    
    else:
        print("❌ Opção inválida!")
    
    print("\n✅ Análise concluída!")