from flask import Flask, request
from playwright.sync_api import sync_playwright
import os
import time
from urllib.parse import urlparse, unquote

app = Flask(__name__)

PASTA = "downloads"
os.makedirs(PASTA, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Motyon Array Download</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #0d0d0f;
            font-family: 'DM Sans', sans-serif;
            color: #e8e8f0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            border-bottom: 1px solid #2a2a35;
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 64px;
            background: #0d0d0f;
        }
        .logo { display: flex; align-items: center; gap: 12px; }
        .logo-icon {
            width: 32px; height: 32px;
            background: #7c6af7;
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
        }
        .logo-icon i { font-size: 17px; color: #fff; }
        .logo-text {
            font-family: 'Syne', sans-serif;
            font-weight: 800;
            font-size: 18px;
            letter-spacing: -0.3px;
            color: #e8e8f0;
        }
        .logo-text span { color: #7c6af7; }
        .status-badge {
            display: flex; align-items: center; gap: 6px;
            background: #141418;
            border: 1px solid #2a2a35;
            border-radius: 20px;
            padding: 5px 12px;
        }
        .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #1d9e75; }
        .status-label { font-size: 12px; color: #6b6b80; }
        main {
            flex: 1;
            display: flex; align-items: center; justify-content: center;
            padding: 3rem 1.5rem;
        }
        .container { width: 100%; max-width: 600px; }
        .hero { text-align: center; margin-bottom: 2.5rem; }
        .hero-tag {
            font-size: 13px; color: #7c6af7;
            letter-spacing: 2px; text-transform: uppercase;
            font-weight: 500; margin-bottom: 12px;
        }
        .hero h1 {
            font-family: 'Syne', sans-serif;
            font-weight: 800; font-size: 34px;
            line-height: 1.15; letter-spacing: -1px; color: #e8e8f0;
        }
        .hero h1 span { color: #7c6af7; }
        .hero p { color: #6b6b80; font-size: 15px; margin-top: 12px; line-height: 1.6; }
        .card {
            background: #141418;
            border: 1px solid #2a2a35;
            border-radius: 16px;
            padding: 2rem;
        }
        .input-label {
            display: block; font-size: 12px; color: #6b6b80;
            letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px;
        }
        .input-row { display: flex; gap: 10px; margin-bottom: 1.5rem; }
        .input-wrap {
            flex: 1; display: flex; align-items: center; gap: 10px;
            background: #1c1c22; border: 1px solid #2a2a35;
            border-radius: 10px; padding: 0 14px; transition: border .2s;
        }
        .input-wrap:focus-within { border-color: #7c6af7; }
        .input-wrap i { font-size: 17px; color: #6b6b80; flex-shrink: 0; }
        .input-wrap input {
            flex: 1; background: transparent; border: none; outline: none;
            color: #e8e8f0; font-size: 14px;
            font-family: 'DM Sans', sans-serif; padding: 13px 0;
        }
        .input-wrap input::placeholder { color: #6b6b80; }
        .btn-clear { display: none; background: none; border: none; cursor: pointer; padding: 0; color: #6b6b80; }
        .btn-capture {
            background: #7c6af7; border: none; border-radius: 10px;
            padding: 0 22px; cursor: pointer; color: #fff;
            font-family: 'Syne', sans-serif; font-weight: 700;
            font-size: 14px; letter-spacing: 0.3px;
            display: flex; align-items: center; gap: 8px;
            white-space: nowrap; transition: opacity .2s;
        }
        .btn-capture:hover { opacity: 0.85; }
        .btn-capture:disabled { opacity: 0.5; cursor: not-allowed; }
        #statusBox {
            display: none; background: #1c1c22;
            border-radius: 10px; padding: 14px 16px; border: 1px solid #2a2a35;
        }
        #loadingState { display: flex; align-items: center; gap: 12px; }
        .spinner {
            width: 18px; height: 18px;
            border: 2px solid #2a2a35; border-top-color: #7c6af7;
            border-radius: 50%; animation: spin .8s linear infinite; flex-shrink: 0;
        }
        #statusMsg { font-size: 14px; color: #6b6b80; }
        #successState { display: none; }
        .success-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
        .success-header i { font-size: 18px; color: #1d9e75; }
        .success-header span { font-size: 14px; color: #e8e8f0; font-weight: 500; }
        .audio-wrap { background: #0d0d0f; border-radius: 8px; padding: 12px; }
        #audioUrl { font-size: 11px; color: #6b6b80; word-break: break-all; margin-bottom: 10px; }
        audio { width: 100%; height: 36px; }
        .btn-link {
            margin-top: 12px; width: 100%;
            background: #1c1c22; border: 1px solid #2a2a35;
            border-radius: 8px; padding: 10px; cursor: pointer;
            color: #a695ff; font-family: 'DM Sans', sans-serif;
            font-size: 13px; font-weight: 500;
            display: flex; align-items: center; justify-content: center; gap: 6px;
            text-decoration: none; transition: background .2s;
        }
        .btn-link:hover { background: #252530; }
        #errorState { display: none; align-items: center; gap: 10px; }
        #errorState i { font-size: 18px; color: #e24b4a; }
        #errorMsg { font-size: 14px; color: #e24b4a; }
        .features {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 12px; margin-top: 1.5rem;
        }
        .feature-item {
            background: #141418; border: 1px solid #2a2a35;
            border-radius: 12px; padding: 1rem; text-align: center;
        }
        .feature-item i { font-size: 20px; color: #7c6af7; display: block; margin-bottom: 8px; }
        .feature-item p { font-size: 12px; color: #6b6b80; line-height: 1.5; }
        footer { border-top: 1px solid #2a2a35; padding: 1rem 2rem; text-align: center; }
        footer p { font-size: 12px; color: #6b6b80; }
        footer span { color: #7c6af7; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>

    <header>
        <div class="logo">
            <div class="logo-icon"><i class="ti ti-music"></i></div>
            <span class="logo-text">Motyon Array <span>Download</span></span>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span>
            <span class="status-label">Servidor ativo</span>
        </div>
    </header>

    <main>
        <div class="container">

            <div class="hero">
                <p class="hero-tag">Motion Array Preview</p>
                <h1>Extraia o áudio<br><span>em segundos</span></h1>
                <p>Cole o link da página e capture o preview em MP3.</p>
            </div>

            <div class="card">
                <label class="input-label">Link da página</label>
                <div class="input-row">
                    <div class="input-wrap" id="inputWrap">
                        <i class="ti ti-link"></i>
                        <input id="urlInput" type="text" placeholder="https://motionarray.com/..." />
                        <button class="btn-clear" id="clearBtn" onclick="clearInput()">
                            <i class="ti ti-x" style="font-size:15px;"></i>
                        </button>
                    </div>
                    <button class="btn-capture" id="mainBtn" onclick="capturar()">
                        <i class="ti ti-player-play" style="font-size:16px;"></i>
                        Capturar
                    </button>
                </div>

                <div id="statusBox">
                    <div id="loadingState">
                        <div class="spinner"></div>
                        <span id="statusMsg">Abrindo página...</span>
                    </div>
                    <div id="successState">
                        <div class="success-header">
                            <i class="ti ti-check"></i>
                            <span>Áudio encontrado!</span>
                        </div>
                        <div class="audio-wrap">
                            <p id="audioUrl"></p>
                            <audio id="audioPlayer" controls></audio>
                        </div>
                        <a id="downloadLink" href="#" target="_blank" class="btn-link">
                            <i class="ti ti-download" style="font-size:15px;"></i>
                            Abrir link do áudio
                        </a>
                    </div>
                    <div id="errorState">
                        <i class="ti ti-alert-circle"></i>
                        <span id="errorMsg"></span>
                    </div>
                </div>
            </div>

            <div class="features">
                <div class="feature-item">
                    <i class="ti ti-world"></i>
                    <p>Detecta MP3<br>automaticamente</p>
                </div>
                <div class="feature-item">
                    <i class="ti ti-click"></i>
                    <p>Clique automático<br>no play</p>
                </div>
                <div class="feature-item">
                    <i class="ti ti-headphones"></i>
                    <p>Preview em<br>alta qualidade</p>
                </div>
            </div>

        </div>
    </main>

    <footer>
        <p>Motyon Array Download — rodando em <span>127.0.0.1:5000</span></p>
    </footer>

    <script>
        const urlInput = document.getElementById('urlInput');
        const clearBtn = document.getElementById('clearBtn');

        urlInput.addEventListener('input', () => {
            clearBtn.style.display = urlInput.value ? 'block' : 'none';
        });

        function clearInput() {
            urlInput.value = '';
            clearBtn.style.display = 'none';
            urlInput.focus();
            hideStatus();
        }

        function hideStatus() {
            document.getElementById('statusBox').style.display = 'none';
            document.getElementById('successState').style.display = 'none';
            document.getElementById('errorState').style.display = 'none';
            document.getElementById('loadingState').style.display = 'flex';
        }

        function showLoading(msg) {
            document.getElementById('statusBox').style.display = 'block';
            document.getElementById('loadingState').style.display = 'flex';
            document.getElementById('successState').style.display = 'none';
            document.getElementById('errorState').style.display = 'none';
            document.getElementById('statusMsg').textContent = msg;
        }

        function showSuccess(audioUrl) {
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('errorState').style.display = 'none';
            document.getElementById('successState').style.display = 'block';
            document.getElementById('audioUrl').textContent = audioUrl;
            document.getElementById('audioPlayer').src = audioUrl;
            document.getElementById('downloadLink').href = audioUrl;
        }

        function showError(msg) {
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('successState').style.display = 'none';
            document.getElementById('errorState').style.display = 'flex';
            document.getElementById('errorMsg').textContent = msg;
        }

        async function capturar() {
            const url = urlInput.value.trim();
            if (!url) { urlInput.focus(); return; }

            const btn = document.getElementById('mainBtn');
            btn.disabled = true;

            showLoading('Abrindo página...');

            const msgs = [
                'Abrindo página...',
                'Aguardando carregamento...',
                'Tentando clicar no play...',
                'Capturando áudio...'
            ];
            let i = 0;
            const interval = setInterval(() => {
                i = (i + 1) % msgs.length;
                const el = document.getElementById('statusMsg');
                if (el) el.textContent = msgs[i];
            }, 2500);

            try {
                const formData = new FormData();
                formData.append('url', url);

                const res = await fetch('/', { method: 'POST', body: formData });
                const html = await res.text();

                clearInterval(interval);

                const audioMatch = html.match(/AUDIO_URL:([^\s<]+)/);
                if (audioMatch) {
                    showSuccess(audioMatch[1]);
                } else if (html.includes('ERRO:')) {
                    const errMatch = html.match(/ERRO:(.+)/);
                    showError(errMatch ? errMatch[1].trim() : 'Erro desconhecido.');
                } else {
                    showError('Resposta inesperada do servidor.');
                }
            } catch(e) {
                clearInterval(interval);
                showError('Erro de conexão com o servidor.');
            }

            btn.disabled = false;
        }

        urlInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') capturar();
        });
    </script>

</body>
</html>
"""


def nome_arquivo(audio_url):
    path = unquote(urlparse(audio_url).path)
    nome = os.path.basename(path)
    if nome.endswith(".mp3"):
        return nome
    return f"audio_{int(time.time())}.mp3"


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "GET":
        return HTML

    pagina_url = request.form["url"]
    audio_url = None

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            args=["--window-position=-32000,-32000"]
        )

        page = browser.new_page()

        def detectar(response):
            nonlocal audio_url
            try:
                url_original = response.url
                url_lower = url_original.lower()
                path = urlparse(url_lower).path

                eh_mp3_real = path.endswith(".mp3")
                nao_e_waveform = "waveform" not in url_lower
                nao_e_json = ".json" not in path

                if eh_mp3_real and nao_e_waveform and nao_e_json:
                    print("\nMP3 ENCONTRADO:", url_original)
                    audio_url = url_original

            except Exception as e:
                print("Erro detectando:", e)

        page.on("response", detectar)

        print("Abrindo página...")

        page.goto(
            pagina_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(3000)

        print("Tentando clicar no play...")

        seletores = [
            "button:has(i.fas.fa-play)",
            "button:has(.fa-play)",
            ".cursor-pointer:has(.fa-play)",
            "button.relative.cursor-pointer"
        ]

        clicou = False

        for seletor in seletores:
            try:
                page.locator(seletor).first.click(timeout=7000)
                print("Clique realizado!")
                clicou = True
                break
            except Exception:
                print(f"Falhou seletor {seletor}")

        if not clicou:
            browser.close()
            return "ERRO:Nao foi possivel clicar no botao play."

        print("Aguardando captura do audio...")

        for _ in range(20):
            if audio_url:
                break
            page.wait_for_timeout(500)

        browser.close()

    if not audio_url:
        return "ERRO:Nenhum audio encontrado. Tente outro link."

    return f"AUDIO_URL:{audio_url}"


if __name__ == "__main__":
    app.run(debug=True)
