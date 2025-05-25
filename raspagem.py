import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import os

# Inicializa o Chrome com stealth
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)
driver.get("https://www8.receita.fazenda.gov.br/simplesnacional/aplicacoes.aspx?id=21")
print("Navegador aberto! Faça a consulta manualmente.")

import tkinter as tk
import threading

def acionar_raspagem():
    janela.destroy()
    # Após clicar, executa a raspagem
    from bs4 import BeautifulSoup
    status = None
    cor = 'black'
    # 1. Tenta extrair do HTML principal
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    for div in soup.find_all('div', class_='panel-body'):
        textos = div.find_all(string=True, recursive=False)
        for idx, t in enumerate(textos):
            if 'Situação no Simples Nacional:' in t:
                spans = div.find_all('span', class_='spanValorVerde')
                if spans:
                    status = spans[0].get_text(strip=True)
                break
        if status:
            break
    # 2. Se não achou, tenta em cada frame
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    if not status:
        for idx, frame in enumerate(frames):
            driver.switch_to.default_content()
            driver.switch_to.frame(idx)
            html_frame = driver.page_source
            soup = BeautifulSoup(html_frame, 'html.parser')
            for div in soup.find_all('div', class_='panel-body'):
                textos = div.find_all(string=True, recursive=False)
                for idx2, t in enumerate(textos):
                    if 'Situação no Simples Nacional:' in t:
                        spans = div.find_all('span', class_='spanValorVerde')
                        if spans:
                            status = spans[0].get_text(strip=True)
                        break
                if status:
                    break
            if status:
                break
        driver.switch_to.default_content()
    # 3. Exibe resultado
    if status:
        if 'não optante' in status.lower() or 'nao optante' in status.lower():
            print(f'\033[91mSituação no Simples Nacional: {status}\033[0m')
            cor = 'red'
        else:
            print(f'\033[92mSituação no Simples Nacional: {status}\033[0m')
            cor = 'green'
        try:
            janela2 = tk.Toplevel(root)
            janela2.title('Situação no Simples Nacional')
            largura, altura = 950, 260  # aumentada a largura e altura
            x = (janela2.winfo_screenwidth() // 2) - (largura // 2)
            y = (janela2.winfo_screenheight() // 2) - (altura // 2)
            janela2.geometry(f'{largura}x{altura}+{x}+{y}')
            janela2.configure(bg='white')
            janela2.attributes('-topmost', True)
            janela2.focus_force()

            # Função para fechar navegador ao fechar janela
            def fechar_janela2():
                try:
                    driver.quit()
                except Exception:
                    pass
                janela2.destroy()
                os._exit(0)  # Encerra todo o processo Python imediatamente

            janela2.protocol("WM_DELETE_WINDOW", fechar_janela2)

            # Ajuste dinâmico do tamanho da fonte
            texto_resultado = f'Situação no Simples Nacional:\n{status}'
            comprimento = len(texto_resultado)
            if comprimento > 90:
                tamanho_fonte = 16
            elif comprimento > 60:
                tamanho_fonte = 20
            else:
                tamanho_fonte = 24

            label = tk.Label(
                janela2,
                text=texto_resultado,
                font=('Arial', tamanho_fonte, 'bold'),
                fg=cor,
                bg='white',
                wraplength=largura-80,  # wrap acompanhando largura da janela
                justify='center',
                anchor='center'
            )
            label.pack(expand=True, fill='both', padx=30, pady=30)
            # Fecha apenas o navegador automaticamente após 1 segundo
            def fechar_navegador_automaticamente():
                try:
                    driver.quit()
                except Exception:
                    pass
            janela2.after(1000, fechar_navegador_automaticamente)
            janela2.grab_set()  # Bloqueia interação com outras janelas enquanto esta estiver aberta
            janela2.focus_force()
            # Mantém a janela aberta até o usuário fechar manualmente
            def fechar_janela2():
                try:
                    driver.quit()
                except Exception:
                    pass
                janela2.destroy()
                os._exit(0)  # Encerra todo o processo Python imediatamente
            janela2.protocol("WM_DELETE_WINDOW", fechar_janela2)
            janela2.mainloop()
        except Exception as e:
            print(f'Não foi possível exibir popup visual: {e}')
            try:
                driver.quit()
            except Exception:
                pass
            root.quit()  # Encerra o mainloop principal do tkinter
    else:
        print('Informação sobre situação no Simples Nacional não encontrada!')

# Mostra a janela logo no início
def finalizar_tudo():
    try:
        driver.quit()
    except Exception:
        pass
    try:
        root.quit()
    except Exception:
        pass
    os._exit(0)  # Encerra todo o processo Python imediatamente

root = tk.Tk()
root.withdraw()
janela = tk.Toplevel()
janela.title('Aguardando ação do usuário')
largura, altura = 500, 180
x = (janela.winfo_screenwidth() // 2) - (largura // 2)
y = (janela.winfo_screenheight() // 2) - (altura // 2)
janela.geometry(f'{largura}x{altura}+{x}+{y}')
janela.configure(bg='white')
janela.attributes('-topmost', True)
janela.focus_force()
label = tk.Label(
    janela,
    text='Quando a página de resultados estiver carregada, clique no botão abaixo para raspar os dados.',
    font=('Arial', 14),
    bg='white',
    wraplength=450,
    justify='center',
    anchor='center'
)
label.pack(expand=True, fill='both', padx=20, pady=20)
botao = tk.Button(janela, text='Raspar Dados', font=('Arial', 16, 'bold'), bg='#1976D2', fg='white', command=acionar_raspagem)
botao.pack(pady=10)
janela.protocol("WM_DELETE_WINDOW", finalizar_tudo)

try:
    janela.mainloop()
finally:
    finalizar_tudo()
    print("Programa finalizado corretamente.")
# Não executar root.mainloop() novamente, pois já foi executado anteriormente e todas as janelas já foram tratadas.
# O navegador é fechado dentro das funções de callback, garantindo que não fique aberto em caso de erro ou fechamento manual.
