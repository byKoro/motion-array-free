from flask import Flask, request, send_file
from playwright.sync_api import sync_playwright
import os
import time
from urllib.parse import urlparse, unquote

app = Flask(__name__)

PASTA = "downloads"
os.makedirs(PASTA, exist_ok=True)

HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d0d0f;
  --surface:#141418;
  --surface2:#1c1c22;
  --border:#2a2a35;
  --accent:#7c6af7;
  --accent2:#a695ff;
  --text:#e8e8f0;
  --muted:#6b6b80;
  --success:#1d9e75;
}
body{background:var(--bg);font-family:'DM Sans',sans-serif;color:var(--text);min-height:100vh}
</style>

<div style="min-height:100vh;background:#0d0d0f;font-family:'DM Sans',sans-serif;color:#e8e8f0;display:flex;flex-direction:column;">

  <header style="border-bottom:1px solid #2a2a35;padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:64px;background:#0d0d0f;">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="width:32px;height:32px;background:#7c6af7;border-radius:8px;display:flex;align-items:center;justify-content:center;">
        <i class="ti ti-music" style="font-size:17px;color:#fff;" aria-hidden="true"></i>
      </div>
      <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:18px;letter-spacing:-0.3px;color:#e8e8f0;">Motyon Array <span style="color:#7c6af7;">Download</span></span>
    </div>
    <div style="display:flex;align-items:center;gap:6px;background:#141418;border:1px solid #2a2a35;border-radius:20px;padding:5px 12px;">
      <span style="width:7px;height:7px;border-radius:50%;background:#1d9e75;display:inline-block;"></span>
      <span style="font-size:12px;color:#6b6b80;">Servidor ativo</span>
    </div>
  </header>

  <main style="flex:1;display:flex;align-items:center;justify-content:center;padding:3rem 1.5rem;">
    <div style="width:100%;max-width:600px;">

      <div style="text-align:center;margin-bottom:2.5rem;">
        <p style="font-size:13px;color:#7c6af7;letter-spacing:2px;text-transform:uppercase;font-weight:500;margin-bottom:12px;">Motion Array Preview</p>
        <h1 style="font-family:'Syne',sans-serif;font-weight:800;font-size:34px;line-height:1.15;letter-spacing:-1px;color:#e8e8f0;">Extraia o áudio<br><span style="color:#7c6af7;">em segundos</span></h1>
        <p style="color:#6b6b80;font-size:15px;margin-top:12px;line-height:1.6;">Cole o link da página e capture o preview em MP3.</p>
      </div>

      <div style="background:#141418;border:1px solid #2a2a35;border-radius:16px;padding:2rem;">

        <label style="display:block;font-size:12px;color:#6b6b80;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;">Link da página</label>

        <div style="display:flex;gap:10px;margin-bottom:1.5rem;">
          <div style="flex:1;display:flex;align-items:center;gap:10px;background:#1c1c22;border:1px solid #2a2a35;border-radius:10px;padding:0 14px;transition:border .2s;" id="inputWrap">
            <i class="ti ti-link" style="font-size:17px;color:#6b6b80;flex-shrink:0;" aria-hidden="true"></i>
            <input
              id="urlInput"
              type="text"
              placeholder="https://motionarray.com/..."
              style="flex:1;background:transparent;border:none;outline:none;color:#e8e8f0;font-size:14px;font-family:'DM Sans',sans-serif;padding:13px 0;"
              onfocus="document.getElementById('inputWrap').style.borderColor='#7c6af7'"
              onblur="document.getElementById('inputWrap').style.borderColor='#2a2a35'"
            >
            <button onclick="clearInput()" id="clearBtn" style="display:none;background:none;border:none;cursor:pointer;padding:0;color:#6b6b80;">
              <i class="ti ti-x" style="font-size:15px;" aria-hidden="true"></i>
            </button>
          </div>

          <button onclick="capturar()" id="mainBtn" style="background:#7c6af7;border:none;border-radius:10px;padding:0 22px;cursor:pointer;color:#fff;font-family:'Syne',sans-serif;font-weight:700;font-size:14px;letter-spacing:0.3px;display:flex;align-items:center;gap:8px;white-space:nowrap;transition:opacity .2s;">
            <i class="ti ti-player-play" style="font-size:16px;" aria-hidden="true"></i>
            Capturar
          </button>
        </div>

        <div id="statusBox" style="display:none;background:#1c1c22;border-radius:10px;padding:14px 16px;border:1px solid #2a2a35;">
          <div id="loadingState" style="display:flex;align-items:center;gap:12px;">
            <div id="spinner" style="width:18px;height:18px;border:2px solid #2a2a35;border-top-color:#7c6af7;border-radius:50%;animation:spin .8s linear infinite;flex-shrink:0;"></div>
            <span id="statusMsg" style="font-size:14px;color:#6b6b80;">Abrindo página...</span>
          </div>
          <div id="successState" style="display:none;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
              <i class="ti ti-check" style="font-size:18px;color:#1d9e75;" aria-hidden="true"></i>
              <span style="font-size:14px;color:#e8e8f0;font-weight:500;">Áudio encontrado!</span>
            </div>
            <div id="audioWrap" style="background:#0d0d0f;border-radius:8px;padding:12px;">
              <p id="audioUrl" style="font-size:11px;color:#6b6b80;word-break:break-all;margin-bottom:10px;"></p>
              <audio id="audioPlayer" controls style="width:100%;height:36px;"></audio>
            </div>
            <a id="downloadLink" href="#" target="_blank">
              <button style="margin-top:12px;width:100%;background:#1c1c22;border:1px solid #2a2a35;border-radius:8px;padding:10px;cursor:pointer;color:#a695ff;font-family:'DM Sans',sans-serif;font-size:13px;font-weight:500;display:flex;align-items:center;justify-content:center;gap:6px;">
                <i class="ti ti-download" style="font-size:15px;" aria-hidden="true"></i>
                Abrir link do áudio
              </button>
            </a>
          </div>
          <div id="errorState" style="display:none;align-items:center;gap:10px;">
            <i class="ti ti-alert-circle" style="font-size:18px;color:#e24b4a;" aria-hidden="true"></i>
            <span id="errorMsg" style="font-size:14px;color:#e24b4a;"></span>
          </div>
        </div>

      </div>

      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:1.5rem;">
        <div style="background:#141418;border:1px solid #2a2a35;border-radius:12px;padding:1rem;text-align:center;">
          <i class="ti ti-world" style="font-size:20px;color:#7c6af7;display:block;margin-bottom:8px;" aria-hidden="true"></i>
          <p style="font-size:12px;color:#6b6b80;line-height:1.5;">Detecta MP3<br>automaticamente</p>
        </div>
        <div style="background:#141418;border:1px solid #2a2a35;border-radius:12px;padding:1rem;text-align:center;">
          <i class="ti ti-click" style="font-size:20px;color:#7c6af7;display:block;margin-bottom:8px;" aria-hidden="true"></i>
          <p style="font-size:12px;color:#6b6b80;line-height:1.5;">Clique automático<br>no play</p>
        </div>
        <div style="background:#141418;border:1px solid #2a2a35;border-radius:12px;padding:1rem;text-align:center;">
          <i class="ti ti-headphones" style="font-size:20px;color:#7c6af7;display:block;margin-bottom:8px;" aria-hidden="true"></i>
          <p style="font-size:12px;color:#6b6b80;line-height:1.5;">Preview em<br>alta qualidade</p>
        </div>
      </div>

    </div>
  </main>

  <footer style="border-top:1px solid #2a2a35;padding:1rem 2rem;text-align:center;">
    <p style="font-size:12px;color:#6b6b80;">Motyon Array Download — rodando em <span style="color:#7c6af7;">127.0.0.1:5000</span></p>
  </footer>

</div>

<style>
@keyframes spin{to{transform:rotate(360deg)}}
</style>

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
  const box = document.getElementById('statusBox');
  box.style.display = 'block';
  document.getElementById('loadingState').style.display = 'flex';
  document.getElementById('successState').style.display = 'none';
  document.getElementById('errorState').style.display = 'none';
  document.getElementById('statusMsg').textContent = msg;
}

function showSuccess(audioUrl) {
  document.getElementById('loadingState').style.display = 'none';
  document.getElementById('errorState').style.display = 'none';
  const ss = document.getElementById('successState');
  ss.style.display = 'block';
  document.getElementById('audioUrl').textContent = audioUrl;
  document.getElementById('audioPlayer').src = audioUrl;
  document.getElementById('downloadLink').href = audioUrl;
}

function showError(msg) {
  document.getElementById('loadingState').style.display = 'none';
  document.getElementById('successState').style.display = 'none';
  const es = document.getElementById('errorState');
  es.style.display = 'flex';
  document.getElementById('errorMsg').textContent = msg;
}

async function capturar() {
  const url = urlInput.value.trim();
  if (!url) { urlInput.focus(); return; }

  const btn = document.getElementById('mainBtn');
  btn.disabled = true;
  btn.style.opacity = '0.6';

  showLoading('Abrindo página...');

  const msgs = ['Abrindo página...', 'Aguardando carregamento...', 'Tentando clicar no play...', 'Capturando áudio...'];
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

    const audioMatch = html.match(/src="([^"]+\.mp3[^"]*)"/);
    const hrefMatch = html.match(/href="(https?:\/\/[^"]+\.mp3[^"]*)"/);
    const found = audioMatch?.[1] || hrefMatch?.[1];

    if (found) {
      showSuccess(found);
    } else if (html.includes('Nenhum áudio')) {
      showError('Nenhum áudio encontrado. Tente outro link.');
    } else if (html.includes('clicar no botão')) {
      showError('Não foi possível clicar no play. Tente novamente.');
    } else {
      showError('Resposta inesperada do servidor.');
    }
  } catch(e) {
    clearInterval(interval);
    showError('Erro de conexão com o servidor.');
  }

  btn.disabled = false;
  btn.style.opacity = '1';
}

urlInput.addEventListener('keydown', e => { if (e.key === 'Enter') capturar(); });
</script>
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

        # monitora respostas da rede
        def detectar(response):
            nonlocal audio_url

            try:
                url_original = response.url
                url_lower = url_original.lower()
                path = urlparse(url_lower).path

                content_type = response.headers.get("content-type", "").lower()

                eh_mp3_real = path.endswith(".mp3")
                nao_e_waveform = "waveform" not in url_lower
                nao_e_json = ".json" not in path

                if eh_mp3_real and nao_e_waveform and nao_e_json:
                    print("\nMP3 REAL ENCONTRADO:")
                    print(url_original)
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

            # botão do play
            "button:has(i.fas.fa-play)",

            # fallback
            "button:has(.fa-play)",

            # fallback
            ".cursor-pointer:has(.fa-play)",

            # fallback
            "button.relative.cursor-pointer"
        ]

        clicou = False

        for seletor in seletores:

            try:

                page.locator(
                    seletor
                ).first.click(
                    timeout=7000
                )

                print("Clique realizado!")

                clicou = True

                break

            except Exception as e:

                print(
                    f"Falhou seletor {seletor}"
                )

        if not clicou:
            browser.close()

            return """
            Não consegui clicar no botão play.
            """

        print("Aguardando captura do áudio...")

        for _ in range(20):

            if audio_url:
                break

            page.wait_for_timeout(500)

        browser.close()

    if not audio_url:

        return """
        Nenhum áudio encontrado.
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Arial;padding:40px">

        <h2>Áudio encontrado:</h2>

        <p>
            <a href="{audio_url}" target="_blank">
                {audio_url}
            </a>
        </p>

        <br>

        <audio controls autoplay src="{audio_url}" style="width:700px"></audio>

        <br><br>

        <a href="/">
            <button style="padding:10px 18px; cursor:pointer;">
                Baixar outra música
            </button>
        </a>

    </body>
    </html>
    """

if __name__ == "__main__":

    app.run(
        debug=True
    )