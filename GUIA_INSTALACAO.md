# ⚡ AIra9Touch v3.0 ULTRA — Guia Completo de Instalação e Uso

> Edição Cruzeiro · IA · Voz · HUD · Macros · Clipboard · Multi-Perfis · Monitor de Hardware
> 100% Gratuito

---

## 📁 Estrutura de arquivos

```
pasta_do_projeto/
├── aira9touch_v3.py        ← Código principal (NOVO)
├── requirements.txt        ← Dependências Python
├── installer_script.nsi    ← Script do instalador (NSIS)
├── desinstalar_aira9.bat   ← Desinstalador rápido
└── icon.ico                ← Ícone (opcional — crie ou baixe um)
```

---

## 🛠️ PASSO A PASSO — INSTALAÇÃO DO ZERO

### ETAPA 1 · Instalar o Python (se ainda não tiver)

1. Acesse: https://www.python.org/downloads/
2. Baixe o **Python 3.11** (mais estável para todas as libs)
3. Na instalação, marque obrigatoriamente:
   - ✅ **Add Python to PATH**
   - ✅ **Install for all users**
4. Clique em **Install Now**

> **Verificar:** Abra o CMD e digite:
> ```
> python --version
> ```
> Deve aparecer: `Python 3.11.x`

---

### ETAPA 2 · Baixar ou clonar os arquivos do projeto

Coloque todos os arquivos numa pasta, por exemplo:
```
C:\Users\SeuNome\AIra9Touch\
```

---

### ETAPA 3 · Instalar as dependências

Abra o CMD **dentro da pasta do projeto** e execute:

```cmd
pip install -r requirements.txt
```

Aguarde instalar tudo. Deve levar 1–3 minutos.

---

### ETAPA 4 · Instalar o PyAudio (para Comandos de Voz)

O PyAudio exige um passo extra no Windows:

**Opção A — pip direto (tente primeiro):**
```cmd
pip install pyaudio
```

**Opção B — se der erro no pip (recomendada no Windows):**
1. Acesse: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Baixe o arquivo `.whl` para a sua versão do Python. Exemplo:
   ```
   PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
   ```
3. Instale com:
   ```cmd
   pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
   ```

Depois instale o SpeechRecognition:
```cmd
pip install SpeechRecognition
```

> ⚠️ Se não quiser usar Voz, **pule esta etapa** — o app funciona normalmente sem ela.

---

### ETAPA 5 · Rodar o app

```cmd
python aira9touch_v3.py
```

O app abrirá com a interface principal e um ícone na **bandeja do sistema** (barra de tarefas, canto inferior direito).

---

### ETAPA 6 (Opcional) · Gerar o .EXE com PyInstaller

Para ter um executável sem precisar do Python instalado:

```cmd
pip install pyinstaller

pyinstaller --onefile --windowed --icon=icon.ico --name=aira9touch_v3 aira9touch_v3.py
```

O `.exe` ficará em `dist\aira9touch_v3.exe`.

---

### ETAPA 7 (Opcional) · Gerar o Instalador com NSIS

Para distribuir como um instalador `.exe` profissional:

1. Baixe o NSIS: https://nsis.sourceforge.io/Download
2. Instale normalmente
3. Coloque o `aira9touch_v3.exe` (gerado pelo PyInstaller) na pasta junto com o `installer_script.nsi`
4. Clique com o botão direito em `installer_script.nsi` → **Compile NSIS Script**
5. Será gerado: `AIra9Touch_v3_Setup.exe` ✅

---

## 🚀 USANDO OS 7 RECURSOS

---

### ⚡ 1. ATALHOS DE TECLADO (aba ⚡ ATALHOS)

| Botão             | O que faz                                      |
|-------------------|------------------------------------------------|
| + PROGRAMA/ARQ    | Abre qualquer .exe, .pdf, .xlsx etc.           |
| + PASTA           | Abre qualquer pasta no Explorer                |
| + TEXTO AUTO      | Digita um texto automático onde o cursor está  |
| + CLIQUE MOUSE    | Clica numa posição específica da tela          |
| + REPRODUZIR PASTA| Abre o primeiro arquivo de mídia da pasta      |
| + URL / SITE      | Abre qualquer URL no navegador padrão          |

**Como cadastrar:**
1. Clique no botão desejado
2. Selecione o arquivo/pasta ou digite o valor
3. Pressione a combinação de teclas (ex: `Ctrl+Alt+C`)
4. Solte — o atalho é salvo automaticamente ✅

---

### ⏺ 2. GRAVADOR DE MACROS (aba ⏺ MACROS)

**Para gravar:**
1. Digite um nome para a macro (ex: `abrir_sistema`)
2. Clique em **⏺ INICIAR GRAVAÇÃO**
3. Execute qualquer sequência de teclas no teclado
4. Clique em **⏹ PARAR GRAVAÇÃO**
5. A macro é salva com todos os eventos e delays reais

**Para definir um atalho:**
1. Selecione a macro na lista
2. Clique em **🔑 DEFINIR ATALHO**
3. Pressione a combinação de teclas
4. Solte — atalho vinculado ✅

---

### 🤖 3. IA INTEGRADA (aba 🤖 IA)

**Como ativar (100% gratuito com Groq):**

1. Acesse: https://console.groq.com
2. Crie uma conta gratuita
3. Gere uma **API Key** (gratuita, 14.400 req/dia)
4. Na aba IA do app:
   - Cole a API Key no campo **API Key**
   - Deixe a URL padrão: `https://api.groq.com/openai/v1/chat/completions`
   - Modelo: `llama3-8b-8192`
   - Atalho: `ctrl+alt+a` (ou personalize)
5. Clique em **💾 SALVAR CONFIGURAÇÃO**
6. **Ative a chave 🔵** no topo da seção

**Chave on/off:**
- 🔵 Ligada → IA responde via hotkey e pelo chat interno
- ⚫ Desligada → Zero consumo de cota, zero requisições

> ⚠️ A Groq oferece tier gratuito generoso. Desative quando não estiver usando para preservar sua cota.

---

### 🎙 4. COMANDOS DE VOZ (aba 🎙 VOZ)

**Pré-requisito:** PyAudio + SpeechRecognition instalados (ver Etapa 4)

**Como usar:**
1. Ative o switch **COMANDOS DE VOZ**
2. Configure o atalho (padrão: `Ctrl+Alt+V`)
3. Selecione o idioma (`pt-BR` por padrão)
4. Clique em **💾 SALVAR CONFIG DE VOZ**

**Em uso:**
1. Pressione `Ctrl+Alt+V`
2. Fale o nome do atalho (ex: `"Chrome"`, `"Pasta de músicas"`)
3. O app compara o áudio com os nomes dos atalhos cadastrados e executa o mais próximo

> Requer conexão com a internet para o reconhecimento via Google Speech API.

---

### 📋 5. CLIPBOARD INTELLIGENCE (aba ⚙ CONFIG)

Funciona **automaticamente em segundo plano** quando ativado.

| Você copia          | Popup aparece com                          |
|---------------------|--------------------------------------------|
| Telefone celular    | Abrir no WhatsApp · Copiar limpo           |
| E-mail              | Abrir no Gmail · Copiar                    |
| URL (http/https)    | Abrir no navegador · Copiar                |
| CPF                 | Validar CPF (✅ válido / ❌ inválido)      |
| CNPJ                | Consultar na Receita Federal · Copiar      |

O popup aparece no canto superior direito da tela e some sozinho em 8 segundos.

---

### 🖥️ 6. HUD HOLOGRÁFICO (aba ⚙ CONFIG)

**Como ativar:**
1. Ative o switch **HUD HOLOGRÁFICO**
2. Defina o atalho (padrão: `Ctrl+Alt+H`)
3. Clique em **💾 SALVAR ATALHO HUD**

**O HUD mostra:**
- Todos os atalhos ativos do perfil atual (coloridos por tipo)
- CPU% e RAM% em tempo real
- Horário atual

**Para mover:** Clique e arraste o painel para qualquer posição da tela.
**Para fechar:** Clique no ✕ ou pressione o atalho novamente.

---

### 🗂️ 7. MULTI-PERFIS (barra de perfis)

**Como criar um perfil:**
1. Clique em **+ NOVO PERFIL**
2. Digite o nome (ex: `trabalho`, `games`, `estudo`)
3. O novo perfil é criado vazio e ativado automaticamente

**Como trocar de perfil:**
- Use o menu dropdown ao lado de **PERFIL:**
- Cada perfil tem seus próprios atalhos e macros totalmente independentes

**Ideia de uso:**
```
Perfil: trabalho  → Excel, Word, Teams, pastas do trabalho
Perfil: games     → Steam, Discord, OBS, pasta de clips
Perfil: estudo    → Anki, PDFs, YouTube, Notion
```

---

## 📊 MONITOR DE HARDWARE (barra superior)

A barra de stats atualiza automaticamente a cada 2 segundos:

| Indicador | Cor normal   | Cor de alerta      |
|-----------|--------------|--------------------|
| CPU       | Azul neon    | Vermelho (> 80%)   |
| RAM       | Verde neon   | Vermelho (> 85%)   |
| TEMP      | Dourado      | —                  |
| DISCO     | Roxo         | —                  |
| Horário   | Branco       | —                  |

> Temperatura requer suporte do hardware/driver. Em notebooks pode aparecer como N/A.

---

## 🔄 DESINSTALAR

**Opção A — BAT rápido:**
Execute `desinstalar_aira9.bat` como Administrador.

**Opção B — Painel de Controle:**
Painel de Controle → Programas → AIra9Touch → Desinstalar
(disponível se instalou via NSIS)

---

## ❓ PROBLEMAS COMUNS

| Problema                        | Solução                                                                 |
|---------------------------------|-------------------------------------------------------------------------|
| `ModuleNotFoundError`           | Execute `pip install -r requirements.txt` novamente                     |
| Hotkey não funciona             | Execute o app como **Administrador**                                    |
| PyAudio não instala             | Use o arquivo `.whl` manual (ver Etapa 4, Opção B)                      |
| IA retorna erro 401             | API Key incorreta ou expirada — gere uma nova em console.groq.com       |
| IA retorna erro 429             | Cota diária esgotada — aguarde até meia-noite UTC ou desative a IA      |
| Voz não reconhece               | Verifique o microfone e a conexão com a internet                        |
| Temperatura aparece como N/A    | Normal em alguns hardwares — não afeta outras funções                   |
| HUD some ao abrir outra janela  | Normal — é uma janela "always on top"; reabra com o atalho              |

---

## 📦 DEPENDÊNCIAS RESUMIDAS

```
customtkinter   — Interface gráfica premium
Pillow          — Imagens e ícones
keyboard        — Hotkeys globais
pyautogui       — Automação de mouse e teclado
pystray         — Ícone na bandeja do sistema
psutil          — Monitor de CPU/RAM/DISCO/TEMP
pyperclip       — Clipboard Intelligence
requests        — Chamadas à API de IA
SpeechRecognition + pyaudio  — Comandos de Voz (opcional)
```

---

*AIra9Touch v3.0 ULTRA · Edição Cruzeiro · 100% Gratuito*
