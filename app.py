import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pymupdf as fitz
import img2pdf
from PIL import Image

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def pdf_to_images(pdf_path, output_format, output_dir, dpi=200):
    doc = fitz.open(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    saved_files = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=matrix)
        out_path = os.path.join(
            output_dir, f"{base_name}_pagina_{page_index + 1}.{output_format}"
        )

        if output_format in ("jpg", "jpeg"):
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img.save(out_path, "JPEG", quality=95)
        else:
            pix.save(out_path)

        saved_files.append(out_path)

    doc.close()
    return saved_files


def images_to_pdf(image_paths, output_pdf_path):
    converted_images = []
    temp_files = []

    try:
        for path in image_paths:
            if path.lower().endswith((".png",)):
                img = Image.open(path).convert("RGB")
                temp_path = path + "_temp_rgb.jpg"
                img.save(temp_path, "JPEG", quality=95)
                temp_files.append(temp_path)
                converted_images.append(temp_path)
            else:
                converted_images.append(path)

        with open(output_pdf_path, "wb") as f:
            f.write(img2pdf.convert(converted_images))
    finally:
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor PDF <-> Imagem")
        self.geometry("520x420")
        self.resizable(False, False)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.pdf_to_img_tab = ttk.Frame(notebook)
        self.img_to_pdf_tab = ttk.Frame(notebook)

        notebook.add(self.pdf_to_img_tab, text="PDF -> Imagem")
        notebook.add(self.img_to_pdf_tab, text="Imagem -> PDF")

        self._build_pdf_to_img_tab()
        self._build_img_to_pdf_tab()

    # ---------------- PDF -> Imagem ----------------
    def _build_pdf_to_img_tab(self):
        frame = self.pdf_to_img_tab

        ttk.Label(frame, text="Arquivo PDF:").pack(anchor="w", padx=10, pady=(15, 0))
        pdf_row = ttk.Frame(frame)
        pdf_row.pack(fill="x", padx=10, pady=5)

        self.pdf_path_var = tk.StringVar()
        ttk.Entry(pdf_row, textvariable=self.pdf_path_var, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(pdf_row, text="Procurar...", command=self._select_pdf_file).pack(
            side="left", padx=(5, 0)
        )

        ttk.Label(frame, text="Formato de saida:").pack(anchor="w", padx=10, pady=(15, 0))
        self.output_format_var = tk.StringVar(value="png")
        format_row = ttk.Frame(frame)
        format_row.pack(anchor="w", padx=10, pady=5)
        ttk.Radiobutton(format_row, text="PNG", variable=self.output_format_var, value="png").pack(
            side="left", padx=(0, 15)
        )
        ttk.Radiobutton(format_row, text="JPG", variable=self.output_format_var, value="jpg").pack(
            side="left"
        )

        ttk.Label(frame, text="Pasta de destino:").pack(anchor="w", padx=10, pady=(15, 0))
        dest_row = ttk.Frame(frame)
        dest_row.pack(fill="x", padx=10, pady=5)

        self.output_dir_var = tk.StringVar()
        ttk.Entry(dest_row, textvariable=self.output_dir_var, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(dest_row, text="Procurar...", command=self._select_output_dir).pack(
            side="left", padx=(5, 0)
        )

        ttk.Button(
            frame, text="Converter PDF para Imagem", command=self._convert_pdf_to_image
        ).pack(pady=25)

        self.pdf_status_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.pdf_status_var, foreground="green").pack(padx=10)

    def _select_pdf_file(self):
        path = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf")],
        )
        if path:
            self.pdf_path_var.set(path)

    def _select_output_dir(self):
        path = filedialog.askdirectory(title="Selecione a pasta de destino")
        if path:
            self.output_dir_var.set(path)

    def _convert_pdf_to_image(self):
        pdf_path = self.pdf_path_var.get()
        output_dir = self.output_dir_var.get()
        output_format = self.output_format_var.get()

        if not pdf_path:
            messagebox.showwarning("Atencao", "Selecione um arquivo PDF.")
            return
        if not output_dir:
            messagebox.showwarning("Atencao", "Selecione a pasta de destino.")
            return

        try:
            saved_files = pdf_to_images(pdf_path, output_format, output_dir)
            self.pdf_status_var.set(f"{len(saved_files)} imagem(ns) gerada(s) com sucesso!")
            messagebox.showinfo(
                "Sucesso", f"{len(saved_files)} imagem(ns) salva(s) em:\n{output_dir}"
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao converter PDF:\n{exc}")

    # ---------------- Imagem -> PDF ----------------
    def _build_img_to_pdf_tab(self):
        frame = self.img_to_pdf_tab

        ttk.Label(frame, text="Imagens (JPG/PNG):").pack(anchor="w", padx=10, pady=(15, 0))
        img_row = ttk.Frame(frame)
        img_row.pack(fill="x", padx=10, pady=5)

        self.image_paths = []
        self.images_listbox = tk.Listbox(img_row, height=8)
        self.images_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(img_row, orient="vertical", command=self.images_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.images_listbox.config(yscrollcommand=scrollbar.set)

        buttons_row = ttk.Frame(frame)
        buttons_row.pack(fill="x", padx=10, pady=5)
        ttk.Button(buttons_row, text="Adicionar imagens...", command=self._select_images).pack(
            side="left"
        )
        ttk.Button(buttons_row, text="Limpar lista", command=self._clear_images).pack(
            side="left", padx=(5, 0)
        )

        ttk.Label(frame, text="Arquivo PDF de saida:").pack(anchor="w", padx=10, pady=(15, 0))
        pdf_out_row = ttk.Frame(frame)
        pdf_out_row.pack(fill="x", padx=10, pady=5)

        self.output_pdf_var = tk.StringVar()
        ttk.Entry(pdf_out_row, textvariable=self.output_pdf_var, state="readonly").pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(pdf_out_row, text="Salvar como...", command=self._select_output_pdf).pack(
            side="left", padx=(5, 0)
        )

        ttk.Button(
            frame, text="Converter Imagens para PDF", command=self._convert_images_to_pdf
        ).pack(pady=15)

        self.img_status_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.img_status_var, foreground="green").pack(padx=10)

    def _select_images(self):
        paths = filedialog.askopenfilenames(
            title="Selecione as imagens",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")],
        )
        for path in paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                self.images_listbox.insert(tk.END, os.path.basename(path))

    def _clear_images(self):
        self.image_paths = []
        self.images_listbox.delete(0, tk.END)

    def _select_output_pdf(self):
        path = filedialog.asksaveasfilename(
            title="Salvar PDF como",
            defaultextension=".pdf",
            filetypes=[("Arquivo PDF", "*.pdf")],
        )
        if path:
            self.output_pdf_var.set(path)

    def _convert_images_to_pdf(self):
        output_pdf_path = self.output_pdf_var.get()

        if not self.image_paths:
            messagebox.showwarning("Atencao", "Adicione ao menos uma imagem.")
            return
        if not output_pdf_path:
            messagebox.showwarning("Atencao", "Escolha onde salvar o PDF.")
            return

        try:
            images_to_pdf(self.image_paths, output_pdf_path)
            self.img_status_var.set("PDF gerado com sucesso!")
            messagebox.showinfo("Sucesso", f"PDF salvo em:\n{output_pdf_path}")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao converter imagens:\n{exc}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
