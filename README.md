```markdown
# Conversor PDF <-> Imagem

Aplicação desktop com interface gráfica (Tkinter) para converter arquivos PDF em imagens (PNG ou JPG) e imagens em PDF.

## O que foi adicionado

- **`app.py`** — aplicação principal, com janela dividida em duas abas:
  - **PDF -> Imagem**: selecione um arquivo `.pdf` (janela de explorador de arquivos), escolha o formato de saída (**PNG** ou **JPG**) e a pasta de destino. Cada página do PDF é convertida em um arquivo de imagem separado.
  - **Imagem -> PDF**: adicione uma ou várias imagens (`.jpg`, `.jpeg`, `.png`), escolha onde salvar o PDF resultante, e todas as imagens são combinadas em um único arquivo PDF (na ordem em que foram adicionadas).
- **`requirements.txt`** — dependências do projeto: `PyMuPDF`, `Pillow`, `img2pdf`.
- **`ConversorPDF.exe`** — versão compilada da aplicação (via PyInstaller), que roda em Windows sem precisar ter Python instalado. Fica em `dist/ConversorPDF.exe` após a compilação.

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


coloque tuto para baixar
```