#!/usr/bin/env python3
"""
SCRIPT PRINCIPAL DE PRODUÇÃO - ScraperÉtico
Execute este script para rodar em produção de forma segura!
"""

import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import signal

# Importar configurações
from config_producao import *
from src.scraper_etico import ScraperEtico
from src.batch_processor import BatchProcessor

class MonitorProducao:
    def __init__(self):
        self.setup_diretorios()
        self.setup_logging()
        self.setup_scraper()
        self.running = True
        self.setup_signal_handlers()
        
    def setup_diretorios(self):
        """Criar diretórios necessários"""
        for dir_path in [OUTPUT_DIR, BACKUP_DIR, LOG_DIR]:
            Path(dir_path).mkdir(exist_ok=True, parents=True)
        print(f"📁 Diretórios criados: {OUTPUT_DIR}, {BACKUP_DIR}, {LOG_DIR}")
    
    def setup_logging(self):
        """Configurar logging detalhado"""
        log_file = Path(LOG_DIR) / f"producao_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("ProducaoMonitor")
        self.logger.info("🚀 Sistema de monitoramento iniciado")
        
    def setup_scraper(self):
        """Configurar scraper para produção"""
        self.scraper = ScraperEtico(
            user_agent=USER_AGENT,
            default_delay=DEFAULT_DELAY,
            timeout=TIMEOUT
        )
        
        self.batch_processor = BatchProcessor()
        self.batch_processor.scraper = self.scraper
        
        self.logger.info(f"⚙️ Scraper configurado - Delay: {DEFAULT_DELAY}s, Timeout: {TIMEOUT}s")
    
    def setup_signal_handlers(self):
        """Configurar kill switch"""
        def signal_handler(sig, frame):
            self.logger.info("🛑 KILL SWITCH ATIVADO - Parando execução...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def verificar_horario(self):
        """Verificar se está no horário permitido"""
        hora_atual = datetime.now().hour
        if HORARIO_INICIO <= hora_atual <= HORARIO_FIM:
            return True
        else:
            self.logger.warning(f"⏰ Fora do horário permitido: {hora_atual}h (permitido: {HORARIO_INICIO}h-{HORARIO_FIM}h)")
            return False
    
    def executar_lote(self, sites):
        """Executar um lote de sites"""
        self.logger.info(f"🔄 Iniciando lote com {len(sites)} sites")
        
        # Processar lote
        job_state = self.batch_processor.process_batch(
            sites,
            max_workers=MAX_WORKERS,
            show_progress=True
        )
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(OUTPUT_DIR) / f"monitoramento_{timestamp}"
        
        self.batch_processor.export_to_csv(job_state, f"{output_file}.csv")
        self.batch_processor.export_to_json(job_state, f"{output_file}.json")
        
        # Log estatísticas
        sucesso = len(job_state.completed_urls)
        total = job_state.total_urls
        self.logger.info(f"📊 Lote concluído: {sucesso}/{total} sucessos ({(sucesso/total)*100:.1f}%)")
        
        return job_state
    
    def rodar_producao(self):
        """Executar monitoramento de produção"""
        self.logger.info("🎯 INICIANDO MONITORAMENTO DE PRODUÇÃO")
        self.logger.info(f"📋 Sites configurados: {len(SITES_PRODUCAO)}")
        
        if not SITES_PRODUCAO:
            self.logger.error("❌ ERRO: Nenhum site configurado em SITES_PRODUCAO!")
            return
        
        # Verificar se está no horário
        if not self.verificar_horario():
            self.logger.info("⏸️ Aguardando horário permitido...")
            return
        
        try:
            # Executar lote
            job_state = self.executar_lote(SITES_PRODUCAO)
            
            # Pausa entre lotes
            self.logger.info(f"⏸️ Pausa de {PAUSE_ENTRE_LOTES}s antes do próximo lote...")
            time.sleep(PAUSE_ENTRE_LOTES)
            
        except Exception as e:
            self.logger.error(f"💥 ERRO CRÍTICO: {str(e)}")
            raise
        
        self.logger.info("✅ Ciclo de produção concluído")

def main():
    print("🤖 MONITOR DE PRODUÇÃO - ScraperÉtico")
    print("=" * 50)
    print("⚠️  ATENÇÃO: Certifique-se de ter editado config_producao.py!")
    print("🛑 Para parar: Ctrl+C (kill switch)")
    print("=" * 50)
    
    # Verificar se configurações foram editadas
    if "seusite.com" in USER_AGENT or "contato@seusite.com" in USER_AGENT:
        print("❌ ERRO: Você precisa editar config_producao.py primeiro!")
        print("📝 Edite o USER_AGENT com SEU site e email reais!")
        sys.exit(1)
    
    if len(SITES_PRODUCAO) == 0 or "example.com" in str(SITES_PRODUCAO):
        print("❌ ERRO: Configure seus sites reais em SITES_PRODUCAO!")
        sys.exit(1)
    
    # Confirmar início
    resposta = input("🤔 Confirma início da produção? (s/N): ").lower()
    if resposta != 's':
        print("🛑 Produção cancelada")
        sys.exit(0)
    
    # Iniciar monitor
    monitor = MonitorProducao()
    monitor.rodar_producao()

if __name__ == "__main__":
    main()