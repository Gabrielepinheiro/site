"""Monta as páginas do site a partir do index.html (home) e de src/.

O index.html é a fonte do estilo, das fontes, do rodapé e da configuração.
Cada página interna vem de src/paginas/<nome>.html (só o <main>).

Uso: python3 build.py            → gera sobre-mim.html, diagnostico-da-casa.html e consultoria.html
     python3 build.py --previa D  → gera também uma cópia para a prévia em D, com links entre arquivos
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).parent
SITE = 'https://www.gabrielepinheiro.com'

PAGINAS = {
    'home': {'arquivo': 'index.html', 'url': SITE + '/', 'menu': 'Home'},
    'sobre': {'arquivo': 'sobre-mim.html', 'url': SITE + '/sobre-mim', 'menu': 'Sobre mim',
              'titulo': 'Sobre mim · Gabriele Pinheiro',
              'descricao': 'Gabriele Pinheiro, interior designer. Formação, trajetória e o olhar que guia cada projeto.'},
    'diagnostico': {'arquivo': 'diagnostico-da-casa.html', 'url': SITE + '/diagnostico-da-casa', 'menu': 'Diagnóstico da Casa',
                    'titulo': 'Diagnóstico da Casa · Gabriele Pinheiro',
                    'descricao': 'Em cerca de 6 minutos, descubra quais ambientes pesam mais na sua rotina e por qual começar. Gratuito.'},
    'impressum': {'arquivo': 'impressum.html', 'url': SITE + '/impressum', 'menu': None, 'md': 'rechtliches/impressum.md',
                  'titulo': 'Impressum · Gabriele Pinheiro', 'descricao': 'Impressum von Gabriele Pinheiro, Interior designer.'},
    'datenschutz': {'arquivo': 'datenschutz.html', 'url': SITE + '/datenschutz', 'menu': None, 'md': 'rechtliches/datenschutz.md',
                    'titulo': 'Datenschutzerklärung · Gabriele Pinheiro', 'descricao': 'Datenschutzerklärung von Gabriele Pinheiro, Interior designer.'},
    'consultoria': {'arquivo': 'consultoria.html', 'url': SITE + '/consultoria', 'menu': 'Consultoria',
                    'titulo': 'Consultoria · Gabriele Pinheiro',
                    'descricao': 'Como funciona a consultoria de design de interiores online: caminhos, projetos, etapas e prazos.'},
}

COMUM = '''<script id="js-comum">
/* Comum a todas as páginas: menu, links do diagnóstico, links legais, foto e ano */
(function () {
  var C = window.GP_CONFIG || {};
  var nav = document.querySelector(".topo-nav"), botao = nav && nav.querySelector(".menu-botao");
  if (botao) botao.addEventListener("click", function () {
    var aberto = nav.classList.toggle("aberto");
    botao.setAttribute("aria-expanded", String(aberto));
  });
  document.querySelectorAll("[data-link=diagnostico]").forEach(function (a) { if (C.linkDiagnostico) a.href = C.linkDiagnostico; });
  var urls = { impressum: C.impressum, privacidade: C.privacidade };
  document.querySelectorAll("[data-cfg]").forEach(function (el) {
    var u = urls[el.dataset.cfg]; if (!u) return;
    var a = el.tagName === "A" ? el : el.querySelector("a"); a.href = u; el.hidden = false;
  });
  var foto = document.getElementById("foto-sobre");
  if (foto && C.foto) {
    foto.innerHTML = '<img src="' + encodeURI(C.foto) + '" alt="Gabriele Pinheiro">';
    foto.hidden = false; foto.parentElement.classList.add("com-foto");
  }
  var ano = document.getElementById("ano"); if (ano) ano.textContent = new Date().getFullYear();
  if (C.previa) document.querySelectorAll("a[data-pag]").forEach(function (a) {
    if (C.previa[a.dataset.pag]) { a.href = C.previa[a.dataset.pag]; a.removeAttribute("target"); }
  });
  if (C.previa) document.querySelectorAll("a[data-cfg=impressum], a[data-cfg=privacidade]").forEach(function (a) { a.removeAttribute("target"); });
})();
</script>'''


ATUAL = ' aria-current="page"'


def menu(atual):
    itens = ''.join(
        f'<li><a data-pag="{k}" href="{v["url"]}" target="_top"{ATUAL if k == atual else ""}>{v["menu"]}</a></li>'
        for k, v in PAGINAS.items() if v['menu'])
    return ('<!--MENU-->\n<nav class="topo-nav" aria-label="Menu principal"><div class="topo-dentro">'
            f'<a class="marca" data-pag="home" href="{SITE}/" target="_top">Gabriele Pinheiro<small>Interior designer</small></a>'
            '<button type="button" class="menu-botao" aria-expanded="false" aria-controls="menu-lista">Menu</button>'
            f'<ul class="menu" id="menu-lista">{itens}</ul></div></nav>\n<!--/MENU-->')


def trocar(t, padrao, novo, contagem=1):
    t2, n = re.subn(padrao, lambda m: novo, t, flags=re.S)
    assert n == contagem, (padrao[:60], n)
    return t2


def home():
    p = RAIZ / 'index.html'
    t = p.read_text(encoding='utf8')
    css = (RAIZ / 'src/estilo-paginas.css').read_text(encoding='utf8')
    bloco_css = '/*PAGINAS*/\n' + css + '/*/PAGINAS*/\n'
    if '/*PAGINAS*/' in t:
        t = trocar(t, r'/\*PAGINAS\*/.*?/\*/PAGINAS\*/\n', bloco_css)
    else:  # primeira vez: entra no fim do estilo da marca, antes do </style> que fecha o <head>
        i = t.rindex('</style>', 0, t.index('</head>'))
        t = t[:i] + bloco_css + t[i:]
    if '<!--MENU-->' in t:
        t = trocar(t, r'<!--MENU-->.*?<!--/MENU-->', menu('home'))
    else:
        t = t.replace('<body>\n', '<body>\n' + menu('home') + '\n', 1)
    if 'id="js-comum"' in t:
        t = trocar(t, r'<script id="js-comum">.*?</script>', COMUM)
    else:  # logo depois do bloco de configuração
        i = t.index('</script>', t.index('window.GP_CONFIG')) + len('</script>')
        t = t[:i] + '\n' + COMUM + t[i:]
    p.write_text(t, encoding='utf8')
    return t


def md_html(md):
    """Markdown simples dos textos legais: títulos, parágrafos com quebra de linha, listas e negrito."""
    import html
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        return re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', s)
    out = []
    for bloco in re.split(r'\n\s*\n', md.strip()):
        linhas = bloco.split('\n')
        if linhas[0].startswith('# '):
            out.append(f'<h1>{inline(linhas[0][2:])}</h1>')
        elif linhas[0].startswith('## '):
            out.append(f'<h2>{inline(linhas[0][3:])}</h2>')
        elif all(l.startswith('- ') for l in linhas):
            out.append('<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in linhas) + '</ul>')
        else:
            out.append('<p>' + '<br>\n'.join(inline(l) for l in linhas) + '</p>')
    return '\n'.join(out) + '\n'


def pagina(t_home, chave):
    info = PAGINAS[chave]
    cabeca = t_home[:t_home.index('<body>')]
    cabeca = trocar(cabeca, r'<title>.*?</title>', f'<title>{info["titulo"]}</title>')
    cabeca = trocar(cabeca, r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{info["descricao"]}">')
    cabeca = trocar(cabeca, r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{info["titulo"]}">')
    cabeca = trocar(cabeca, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{info["descricao"]}">')
    rodape = re.search(r'<footer class="rodape">.*?</footer>', t_home, re.S).group(0)
    config = re.search(r'<script>\s*/\* =+\s*CONFIGURAÇÃO.*?</script>', t_home, re.S).group(0)
    if info.get('md'):
        corpo = '<main class="pg"><article class="texto-legal" lang="de">\n' + md_html((RAIZ / info['md']).read_text(encoding='utf8')) + '</article></main>\n'
    else:
        corpo = (RAIZ / f'src/paginas/{chave}.html').read_text(encoding='utf8')
    return f'{cabeca}<body>\n{menu(chave)}\n\n{corpo}\n{rodape}\n\n{config}\n{COMUM}\n</body>\n</html>\n'


def estatico(saidas, destino):
    """Site de verdade (sem Embed): pastas com index.html, estilo e fontes em arquivos próprios, links internos relativos."""
    import base64
    destino.mkdir(parents=True, exist_ok=True)
    (destino / 'fonts').mkdir(exist_ok=True)
    pastas = {'home': '', 'sobre': 'sobre-mim', 'diagnostico': 'diagnostico-da-casa', 'consultoria': 'consultoria',
              'impressum': 'impressum', 'datenschutz': 'datenschutz'}
    css = None
    for chave, html in saidas.items():
        estilos = re.findall(r'<style>(.*?)</style>', html[:html.index('</head>')], re.S)
        if css is None:
            css = '\n'.join(estilos)
            def fonte(m):
                familia = re.search(r"font-family: '([^']+)'", m.group(0)).group(1)
                estilo = re.search(r'font-style: (\w+)', m.group(0)).group(1)
                peso = re.search(r'font-weight: ([0-9]+)', m.group(0)).group(1)
                nome = f"{familia.lower().replace(' ', '-')}-{estilo}-{peso}.woff2"
                (destino / 'fonts' / nome).write_bytes(base64.b64decode(m.group(1)))
                return m.group(0).replace(f'data:font/woff2;base64,{m.group(1)}', f'/fonts/{nome}')
            css = re.sub(r'@font-face\s*\{[^}]*?data:font/woff2;base64,([A-Za-z0-9+/=]+)[^}]*\}', fonte, css)
            assert 'base64' not in css
            (destino / 'estilo.css').write_text(css, encoding='utf8')
        cab_fim = html.index('</head>')
        cab = re.sub(r'<style>.*?</style>\s*', '', html[:cab_fim], flags=re.S)
        # impede que o script que a hospedagem do Wix injeta guarde dados no aparelho ou chame a API (sem cookies, sem banner)
        html = cab + '<script>window.wixSiteScript = true;</script>\n<link rel="stylesheet" href="/estilo.css">\n' + html[cab_fim:]
        html = html.replace('href="' + SITE + '/', 'href="/').replace('"' + SITE + '/impressum"', '"/impressum"').replace('"' + SITE + '/datenschutz"', '"/datenschutz"')
        for pg in ('sobre-mim', 'diagnostico-da-casa', 'consultoria', 'impressum', 'datenschutz'):
            html = html.replace(f'href="/{pg}"', f'href="/{pg}.html"').replace(f'"/{pg}"', f'"/{pg}.html"')
        nome = (pastas[chave] or 'index') + '.html'
        (destino / nome).write_text(html, encoding='utf8')


def main():
    t_home = home()
    saidas = {'home': t_home}
    for chave in ('sobre', 'diagnostico', 'consultoria', 'impressum', 'datenschutz'):
        html = pagina(t_home, chave)
        (RAIZ / PAGINAS[chave]['arquivo']).write_text(html, encoding='utf8')
        saidas[chave] = html
    if '--previa' in sys.argv:
        destino = Path(sys.argv[sys.argv.index('--previa') + 1])
        destino.mkdir(parents=True, exist_ok=True)
        mapa = {'home': 'home.html', 'sobre': 'sobre-mim.html', 'diagnostico': 'diagnostico-da-casa.html', 'consultoria': 'consultoria.html', 'impressum': 'impressum.html', 'datenschutz': 'datenschutz.html'}
        js = 'window.GP_CONFIG.previa = ' + str(mapa).replace("'", '"') + '; window.GP_CONFIG.impressum = "impressum.html"; window.GP_CONFIG.privacidade = "datenschutz.html";'
        for chave, html in saidas.items():
            html = html.replace('\n</script>\n<script id="js-comum">', '\n' + js + '\n</script>\n<script id="js-comum">', 1)
            (destino / mapa[chave]).write_text(html, encoding='utf8')
        # a página principal da prévia é a home, sem o esqueleto do documento
        h = (destino / 'home.html').read_text(encoding='utf8')
        cab = re.search(r'<head>(.*?)</head>', h, re.S).group(1)
        cab = re.sub(r'<meta charset[^>]*>\s*|<meta name="viewport"[^>]*>\s*', '', cab)
        corpo = re.search(r'<body>(.*)</body>', h, re.S).group(1)
        (destino / 'index-previa.html').write_text(cab + corpo, encoding='utf8')
    if '--estatico' in sys.argv:
        estatico(saidas, Path(sys.argv[sys.argv.index('--estatico') + 1]))
    print('ok')


if __name__ == '__main__':
    main()
