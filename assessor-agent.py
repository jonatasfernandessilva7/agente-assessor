import os
import yfinance as yf
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO")
EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
SENHA_APP = os.getenv("SENHA_APP")
VALOR_APORTE = 220.00

print(EMAIL_DESTINO, EMAIL_ORIGEM, SENHA_APP)

# CARTEIRA TEÓRICA COMPLETA 
CORE = {
    "IMOBILIARIO": ["HGLG11.SA", "KNRI11.SA", "HGBS11.SA", "RBVA11.SA", "HGRU11.SA"],
    "PAPEL": ["KNCR11.SA", "MCCI11.SA", "AFHI11.SA"],
    "GLOBAL": ["WRLD11.SA"] 
}

SATELITE = ["SNEL11.SA", "QLBR11.SA", "CHIP11.SA", "HODL11.SA", "HSML11.SA", "FATN11.SA", "TEPP11.SA", "RINV11.SA"]
SEGURANCA = ["B5P211.SA", "AUPO11.SA", "BIAU39.SA"]

class AssessorIA:
    def __init__(self, aporte):
        self.aporte = aporte
        self.data_atual = datetime.now()

    def obter_preco(self, ticker):
        try:
            df = yf.Ticker(ticker).history(period="1d")
            return round(df['Close'].iloc[-1], 2)
        except:
            return 0.0

    def definir_estrategia(self):
        mes = self.data_atual.month

        if mes % 3 == 1:
            alvo_p = CORE["GLOBAL"][0]
            alvo_s = "SNEL11.SA" 
            desc = "Mês de Expansão Global (CORE)"
        
        elif mes % 3 == 2:
            index = (mes // 3) % len(CORE["IMOBILIARIO"])
            alvo_p = CORE["IMOBILIARIO"][index]
            alvo_s = "SNEL11.SA"
            desc = "Mês de Imóveis Físicos (CORE)"
            
        else:
            index = (mes // 3) % len(CORE["PAPEL"])
            alvo_p = CORE["PAPEL"][index]
            alvo_s = "B5P211.SA"
            desc = "Mês de Renda Fixa e Crédito (CORE/SEG)"

        preco_p = self.obter_preco(alvo_p)
        preco_s = self.obter_preco(alvo_s)

        # Cálculo de quantidade
        qtd_p = 1
        sobra = self.aporte - preco_p
        qtd_s = int(sobra // preco_s) if sobra > 0 and preco_s > 0 else 0
        total = (qtd_p * preco_p) + (qtd_s * preco_s)

        return {
            "p_ticker": alvo_p, "p_qtd": qtd_p, "p_preco": preco_p,
            "s_ticker": alvo_s, "s_qtd": qtd_s, "s_preco": preco_s,
            "total": round(total, 2), "estrategia": desc
        }

    def salvar_historico(self, s):
        file = 'historico_aportes.csv'
        novo_registro = {
            'Data': self.data_atual.strftime('%d/%m/%Y'),
            'Estrategia': s['estrategia'],
            'Ativo_1': s['p_ticker'],
            'Qtd_1': s['p_qtd'],
            'Ativo_2': s['s_ticker'],
            'Qtd_2': s['s_qtd'],
            'Investido_R$': s['total']
        }
        df = pd.read_csv(file) if os.path.exists(file) else pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        df.to_csv(file, index=False)

    def enviar_email(self, s):
        msg = EmailMessage()
        corpo = f"""
        🤖 RELATÓRIO DE APORTE MENSAL - {self.data_atual.strftime('%m/%Y')}
        --------------------------------------------------
        Estratégia: {s['estrategia']}
        
        AÇÕES SUGERIDAS:
        1. {s['p_ticker']}: {s['p_qtd']} cota(s) a R$ {s['p_preco']}
        2. {s['s_ticker']}: {s['s_qtd']} cota(s) a R$ {s['p_preco']}
        
        TOTAL DO APORTE: R$ {s['total']}
        SALDO RESTANTE: R$ {round(self.aporte - s['total'], 2)}
        --------------------------------------------------
        Status: Histórico atualizado no GitHub.
        Foco no longo prazo. Faltam aproximadamente 40 anos.
        """
        msg.set_content(corpo)
        msg['Subject'] = f"Assessoria IA: Plano de Aporte {self.data_atual.strftime('%d/%m')}"
        msg['From'] = EMAIL_ORIGEM
        msg['To'] = EMAIL_DESTINO

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ORIGEM, SENHA_APP)
            smtp.send_message(msg)

if __name__ == "__main__":
    assessor = AssessorIA(VALOR_APORTE)
    plano = assessor.definir_estrategia()
    assessor.salvar_historico(plano)
    assessor.enviar_email(plano)
    print("✅ Processo concluído com sucesso.")