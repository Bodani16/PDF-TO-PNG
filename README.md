# Conversor PDF <-> Imagem

Aplicação desktop com interface gráfica (CustomTkinter) para converter arquivos PDF em imagens (PNG ou JPG) e imagens em PDF.

## O que foi adicionado

- **`app.py`** — aplicação principal, com uma barra lateral de navegação e duas telas:
  - **PDF -> Imagem**: selecione um arquivo `.pdf` (janela de explorador de arquivos), escolha o formato de saída (**PNG** ou **JPG**) e a pasta de destino. Cada página do PDF é convertida em um arquivo de imagem separado.
  - **Imagem -> PDF**: adicione uma ou várias imagens (`.jpg`, `.jpeg`, `.png`), escolha onde salvar o PDF resultante, e todas as imagens são combinadas em um único arquivo PDF (na ordem em que foram adicionadas).
- **`requirements.txt`** — dependências do projeto, com versões fixadas: `PyMuPDF==1.28.2`, `Pillow==12.3.0`, `img2pdf==0.6.3`, `customtkinter==6.0.0`.
- **`ConversorPDF.exe`** — versão compilada da aplicação (via PyInstaller), que roda em Windows sem precisar ter Python instalado. Fica em `dist/ConversorPDF.exe` após a compilação.

## Segurança

- Arquivos temporários (usados na conversão de PNG para PDF) são criados com `tempfile.mkstemp` — nome aleatório e criação exclusiva, em vez de um caminho previsível — evitando colisão/condição de corrida quando a pasta é compartilhada por outros usuários ou processos.
- Dependências com versão fixada em `requirements.txt` para builds reprodutíveis e evitar puxar automaticamente uma versão futura comprometida.

## Como usar (código-fonte)

```bash
pip install -r requirements.txt
python app.py
```

## Como usar (executável)

Basta dar duplo clique em `dist/ConversorPDF.exe`. Nenhuma instalação de Python ou bibliotecas é necessária.

## Como recompilar o .exe

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "ConversorPDF" app.py
```

O executável gerado fica na pasta `dist/`.
