import json, os, re, time, html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import parse, request

DATA_DIR = "lessons"
os.makedirs(DATA_DIR, exist_ok=True)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "topic"

def fetch(url: str, timeout: int = 15) -> str:
    req = request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
        },
    )
    with request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(350000)
    return raw.decode("utf-8", errors="ignore")

def strip_html(source: str) -> str:
    source = re.sub(r"(?is)<script.*?>.*?</script>", " ", source)
    source = re.sub(r"(?is)<style.*?>.*?</style>", " ", source)
    source = re.sub(r"(?s)<[^>]+>", " ", source)
    source = html.unescape(source)
    source = re.sub(r"\s+", " ", source)
    return source.strip()

def split_sentences(text: str):
    parts = re.split(r"(?<=[.!?])\s+", text)
    clean = []
    seen = set()
    for p in parts:
        p = p.strip()
        if len(p) < 40 or len(p) > 260:
            continue
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        clean.append(p)
    return clean

def duckduckgo_links(query: str, limit: int = 5):
    url = "https://html.duckduckgo.com/html/?q=" + parse.quote(query + " tech tutorial")
    try:
        page = fetch(url)
    except Exception:
        return []
    hrefs = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', page)
    links = []
    for href in hrefs:
        href = html.unescape(href)
        if href.startswith("//"):
            href = "https:" + href
        if "duckduckgo.com/l/" in href and "uddg=" in href:
            q = parse.urlsplit(href).query
            href = parse.parse_qs(q).get("uddg", [href])[0]
            href = parse.unquote(href)
        if href.startswith("http") and href not in links:
            links.append(href)
        if len(links) >= limit:
            break
    return links

def fallback_links(query: str):
    wiki = "https://en.wikipedia.org/wiki/" + parse.quote(query.replace(" ", "_"))
    search = "https://en.wikipedia.org/w/index.php?search=" + parse.quote(query)
    return [wiki, search]

def research_topic(query: str):
    links = duckduckgo_links(query, limit=5)
    if not links:
        links = fallback_links(query)
    texts = []
    used = []
    for link in links[:5]:
        try:
            txt = strip_html(fetch(link))
            if len(txt) > 500:
                texts.append(txt[:7000])
                used.append(link)
        except Exception:
            continue
    corpus = "\n".join(texts)
    return {"sources": used, "corpus": corpus}

def build_notes(topic: str, level: str, corpus: str, sources):
    sents = split_sentences(corpus)
    topic_words = [w for w in re.findall(r"[a-zA-Z0-9]+", topic.lower()) if len(w) > 2]
    ranked = []
    for s in sents:
        score = 0
        low = s.lower()
        for w in topic_words:
            if w in low:
                score += 3
        for kw in ["used", "allows", "helps", "system", "software", "application", "protocol", "network", "code", "data", "security", "development"]:
            if kw in low:
                score += 1
        ranked.append((score, s))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    chosen = [s for _, s in ranked[:10]] or sents[:10]

    overview = chosen[:3]
    concepts = chosen[3:7]
    use_cases = chosen[7:10]

    md = []
    md.append(f"# {topic.title()}")
    md.append("")
    md.append(f"**Level:** {level.title()}")
    md.append("")
    md.append("## Simple Overview")
    for item in overview:
        md.append(f"- {item}")
    md.append("")
    md.append("## Key Concepts")
    for idx, item in enumerate(concepts, 1):
        md.append(f"{idx}. {item}")
    md.append("")
    md.append("## Real-World Use")
    if use_cases:
        for item in use_cases:
            md.append(f"- {item}")
    else:
        md.append(f"- {topic.title()} is commonly applied in practical software and infrastructure work.")
    md.append("")
    md.append("## What To Practice")
    md.append(f"- Explain {topic} in your own words.")
    md.append(f"- Set up a tiny demo project related to {topic}.")
    md.append(f"- Identify where {topic} fits in a real product.")
    md.append("")
    md.append("## Sources")
    for src in sources:
        md.append(f"- {src}")
    return "\n".join(md)

def build_diagram(topic: str):
    return f"""
+----------------------+
|      LEARN {topic.upper()}      |
+----------------------+
           |
           v
+----------------------+
| 1. What it is        |
| definition & role    |
+----------------------+
           |
           v
+----------------------+
| 2. How it works      |
| flow / components    |
+----------------------+
           |
           v
+----------------------+
| 3. Build a demo      |
| hands-on practice    |
+----------------------+
           |
           v
+----------------------+
| 4. Real use cases    |
| jobs / production    |
+----------------------+
           |
           v
+----------------------+
| 5. Test yourself     |
| quiz + mini lab      |
+----------------------+
""".strip("\n")

def build_mermaid(topic: str):
    safe = topic.replace('"', "'")
    return f"""flowchart TD
    A["{safe}: What it is"] --> B["How it works"]
    B --> C["Main components"]
    C --> D["Build a small demo"]
    D --> E["Real-world use"]
    E --> F["Quiz and review"]
"""

def build_quiz(topic: str):
    return f"""# Quiz: {topic.title()}

1. In simple words, what is {topic}?
2. Why is {topic} important in real software work?
3. Name two components or ideas related to {topic}.
4. Where would you use {topic} in a real project?
5. What problem does {topic} help solve?
6. What could go wrong if {topic} is misunderstood?
7. Describe the flow of {topic} step by step.
8. What tools or languages are often used with {topic}?
9. Give one beginner project for practicing {topic}.
10. Explain {topic} to a non-technical person in 3 sentences.
"""

def build_lab(topic: str):
    return f"""# Practice Lab: {topic.title()}

## Goal
Create a tiny hands-on exercise to understand {topic}.

## Task
1. Search for one real product or app that uses {topic}.
2. Draw its basic flow on paper or in a text file.
3. Build a very small demo related to {topic}.
4. Write down what worked, what failed, and what you learned.
5. Explain how {topic} would behave in production.

## Success Check
- You can explain {topic} clearly.
- You can connect it to a real-world system.
- You can build or sketch a small example.
"""

def save_lesson(topic: str, payload: dict):
    slug = slugify(topic)
    folder = os.path.join(DATA_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    files = {
        "notes.md": payload["notes"],
        "diagram.txt": payload["diagram"],
        "diagram.mmd": payload["mermaid"],
        "quiz.md": payload["quiz"],
        "lab.md": payload["lab"],
        "sources.json": json.dumps(payload["sources"], indent=2),
    }
    for name, content in files.items():
        with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
            f.write(content)

    record = {
        "topic": topic,
        "slug": slug,
        "saved_at": int(time.time()),
        "folder": folder,
        "sources": payload["sources"],
    }

    histfile = os.path.join(DATA_DIR, "history.json")
    history = []
    if os.path.exists(histfile):
        try:
            with open(histfile, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history = [h for h in history if h.get("slug") != slug]
    history.insert(0, record)

    with open(histfile, "w", encoding="utf-8") as f:
        json.dump(history[:30], f, indent=2)

    return record

def read_history():
    histfile = os.path.join(DATA_DIR, "history.json")
    if os.path.exists(histfile):
        try:
            with open(histfile, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

INDEX_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tech Teacher Phone App</title>
<style>
body{font-family:Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:0}
.wrap{max-width:900px;margin:auto;padding:16px}
.card{background:#111827;border:1px solid #334155;border-radius:16px;padding:16px;margin-bottom:16px}
input,select,button{width:100%;box-sizing:border-box;padding:12px;border-radius:12px;border:1px solid #475569;background:#0b1220;color:#e2e8f0}
button{background:#2563eb;border:none;font-weight:700;margin-top:10px}
pre{white-space:pre-wrap;background:#020617;padding:12px;border-radius:12px;overflow:auto}
a{color:#93c5fd}
.small{color:#94a3b8;font-size:14px}
.grid{display:grid;gap:16px}
@media(min-width:900px){.grid{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <h1>Tech Teacher Phone App</h1>
    <p class="small">Type any tech topic. The app researches the web, writes lesson notes, builds a diagram, a quiz, and a practice lab.</p>
    <label>Topic</label>
    <input id="topic" placeholder="e.g. docker networking">
    <label style="display:block;margin-top:10px;">Level</label>
    <select id="level">
      <option>beginner</option>
      <option>intermediate</option>
      <option>advanced</option>
    </select>
    <button onclick="teach()">Generate lesson</button>
    <p id="status" class="small"></p>
  </div>

  <div class="grid">
    <div class="card"><h2>Notes</h2><pre id="notes"></pre></div>
    <div class="card"><h2>Diagram</h2><pre id="diagram"></pre></div>
    <div class="card"><h2>Quiz</h2><pre id="quiz"></pre></div>
    <div class="card"><h2>Practice Lab</h2><pre id="lab"></pre></div>
  </div>

  <div class="card">
    <h2>Sources</h2>
    <div id="sources" class="small"></div>
  </div>

  <div class="card">
    <h2>Saved History</h2>
    <div id="history" class="small"></div>
  </div>
</div>

<script>
async function loadHistory(){
  const r = await fetch('/api/history');
  const data = await r.json();
  const el = document.getElementById('history');
  if(!data.length){ el.innerHTML = 'No saved lessons yet.'; return; }
  el.innerHTML = data.map(x => `<div style="margin-bottom:8px;"><b>${x.topic}</b><br><span>${x.folder}</span></div>`).join('');
}
async function teach(){
  const topic = document.getElementById('topic').value.trim();
  const level = document.getElementById('level').value;
  if(!topic){ alert('Enter a topic'); return; }
  document.getElementById('status').innerText = 'Working... please wait';
  document.getElementById('notes').innerText = '';
  document.getElementById('diagram').innerText = '';
  document.getElementById('quiz').innerText = '';
  document.getElementById('lab').innerText = '';
  document.getElementById('sources').innerHTML = '';
  const r = await fetch('/api/teach', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({topic, level})
  });
  const data = await r.json();
  if(!r.ok){
    document.getElementById('status').innerText = data.error || 'Failed';
    return;
  }
  document.getElementById('status').innerText = 'Done. Saved in ' + data.saved.folder;
  document.getElementById('notes').innerText = data.notes;
  document.getElementById('diagram').innerText = data.diagram;
  document.getElementById('quiz').innerText = data.quiz;
  document.getElementById('lab').innerText = data.lab;
  document.getElementById('sources').innerHTML = (data.sources || []).map(x => `<div><a href="${x}" target="_blank">${x}</a></div>`).join('');
  loadHistory();
}
loadHistory();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, ctype="text/html; charset=utf-8", body=""):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            return self._send(200, "text/html; charset=utf-8", INDEX_HTML)
        if self.path == "/api/history":
            return self._send(200, "application/json; charset=utf-8", json.dumps(read_history()))
        return self._send(404, "application/json; charset=utf-8", json.dumps({"error": "Not found"}))

    def do_POST(self):
        if self.path != "/api/teach":
            return self._send(404, "application/json; charset=utf-8", json.dumps({"error": "Not found"}))
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw or "{}")
            topic = (payload.get("topic") or "").strip()
            level = (payload.get("level") or "beginner").strip()
            if not topic:
                return self._send(400, "application/json; charset=utf-8", json.dumps({"error": "Topic is required"}))

            research = research_topic(topic)
            corpus = research["corpus"] or f"{topic} is a technology topic. Research was limited, so begin with definitions, components, use cases, and hands-on practice."

            result = {
                "notes": build_notes(topic, level, corpus, research["sources"]),
                "diagram": build_diagram(topic),
                "mermaid": build_mermaid(topic),
                "quiz": build_quiz(topic),
                "lab": build_lab(topic),
                "sources": research["sources"],
            }
            saved = save_lesson(topic, result)
            result["saved"] = saved
            return self._send(200, "application/json; charset=utf-8", json.dumps(result))
        except Exception as e:
            return self._send(500, "application/json; charset=utf-8", json.dumps({"error": str(e)}))

if __name__ == "__main__":
    port = 8000
    print(f"Starting on http://127.0.0.1:{port}")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
