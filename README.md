# 🎵 Motyon Array Download

Ferramenta local para capturar o preview em MP3 de músicas do [Motion Array](https://motionarray.com), com interface web escura e moderna rodando direto no seu navegador.

---

## ✨ Como funciona

O script abre uma instância invisível do Chromium, acessa a página da música, clica automaticamente no botão de play e captura a URL do arquivo MP3 que o site carrega — tudo sem intervenção manual.

---

## 📋 Requisitos

- Python 3.8 ou superior
- pip

---

## 🚀 Instalação

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/motyon-array-download.git
cd motyon-array-download
```

**2. Instale as dependências Python**

```bash
pip install flask playwright
```

**3. Instale o navegador do Playwright**

```bash
playwright install chromium
```

---

## ▶️ Como usar

**1. Inicie o servidor**

```bash
python app.py
```

**2. Acesse no navegador**

```
http://127.0.0.1:5000
```

**3. Cole o link da música**

Acesse uma página de música no Motion Array, copie a URL e cole no campo da interface.

**4. Clique em "Capturar"**

O script vai abrir a página em segundo plano, clicar no play e retornar o player com o áudio encontrado.

---

## 🖥️ Iniciar automaticamente com o Windows

Para que o servidor suba toda vez que o PC ligar, sem abrir nenhuma janela:

**1. Crie um arquivo `iniciar.vbs`** na mesma pasta do `app.py`:

```vbs
CreateObject("WScript.Shell").Run "cmd /c python ""C:\CAMINHO\DA\SUA\PASTA\app.py""", 0, False
```

> Substitua `C:\CAMINHO\DA\SUA\PASTA` pelo caminho real da pasta.

**2. Configure o Agendador de Tarefas**

- Abra o **Agendador de Tarefas** (`Win + S` → buscar)
- Clique em **Criar Tarefa...**
- **Geral:** dê um nome (ex: `Motyon Array`) e marque *Executar com privilégios mais altos*
- **Disparadores:** clique em *Novo* → selecione **Na inicialização**
- **Ações:** clique em *Novo* → aponte para o arquivo `iniciar.vbs`
- Clique em **OK**

A partir do próximo boot, o servidor já estará disponível em `http://127.0.0.1:5000` automaticamente.

---

## 🔧 Estrutura do projeto

```
motyon-array-download/
├── app.py          # Servidor Flask + lógica Playwright
├── iniciar.vbs     # Script de inicialização automática (Windows)
└── README.md       # Esta documentação
```

---

## ⚠️ Observações

- Esta ferramenta é para **uso pessoal**. Respeite os termos de uso do Motion Array.
- O Chromium roda **fora da tela** (`--window-position=-32000,-32000`), sem janela visível.
- O servidor **não fica exposto na internet** — só funciona localmente via `127.0.0.1`.

---

## 🛠️ Tecnologias

- [Flask](https://flask.palletsprojects.com/) — servidor web leve em Python
- [Playwright](https://playwright.dev/python/) — automação de navegador
- HTML/CSS/JS puro — interface sem dependências externas de frontend
