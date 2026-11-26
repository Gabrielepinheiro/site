# Site · gabrielepinheiro.com

Página principal do site da Gabriele Pinheiro, interior designer.
Segue o Brand Book GP (nov/2026): Branco, Névoa, Cacau, Bordô e Antúrio; Instrument Serif, Hanken Grotesk, Reenie Beanie e Tinos.

- `index.html`: o site inteiro em um arquivo só (texto, estilo e movimento).
- O botão do Diagnóstico da Casa leva para https://gabrielepinheiro.github.io/Diagnosticodacasa/?s=PERFIL

## Onde ele roda

O site fica no Wix, em www.gabrielepinheiro.com. Para atualizar:
1. No Editor do Wix, abra a página do site e clique no elemento **Incorporar HTML**.
2. Clique em **Inserir código**, apague o código antigo, cole o conteúdo inteiro de `index.html` e clique em **Aplicar**.
3. Publique.

## Configuração

No fim do `index.html`, o bloco `GP_CONFIG` guarda os links. Campo vazio = item escondido:
- `linkDiagnostico`, `pedeSenha`, `instagram`, `portfolio`, `premier`, `foto`
- `impressum` e `privacidade`: obrigatórios na Alemanha
- `whatsapp`: só depois de confirmar o número oficial

## Impressum e Datenschutz

Os textos estão em `rechtliches/`. No Wix, crie duas páginas de texto com os endereços `/impressum` e `/datenschutz` e cole cada texto. O rodapé do site já aponta para elas.
As fontes estão embutidas no `index.html`, então o site não chama os servidores do Google.
