import os
import tempfile

import customtkinter as ctk
from tkinter import filedialog, messagebox

import pymupdf as fitz
import img2pdf
from PIL import Image

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ACCENT = "#5b6cff"
ACCENT_HOVER = "#4756e6"
SUCCESS = "#1fa971"
DANGER = "#e5484d"
MUTED = "#7a7f92"
CARD_BORDER = "#e4e7f0"
SIDEBAR_BG = "#181b27"
SIDEBAR_TEXT = "#9aa0b4"
FONT_FAMILY = "Segoe UI"


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
                temp_fd, temp_path = tempfile.mkstemp(suffix=".jpg", prefix="conversorpdf_")
                os.close(temp_fd)
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


class FieldLabel(ctk.CTkLabel):
    def __init__(self, parent, text, **kwargs):
        super().__init__(
            parent,
            text=text.upper(),
            font=(FONT_FAMILY, 11, "bold"),
            text_color=MUTED,
            anchor="w",
            **kwargs,
        )


class PathField(ctk.CTkFrame):
    """Read-only path display + browse button, styled as one rounded control."""

    def __init__(self, parent, textvariable, button_text, command):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self,
            textvariable=textvariable,
            state="readonly",
            height=42,
            corner_radius=10,
            border_width=1,
            border_color=CARD_BORDER,
            fg_color="#ffffff",
            text_color="#1a1d29",
            font=(FONT_FAMILY, 11),
        )
        self.entry.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            self,
            text=button_text,
            command=command,
            width=110,
            height=42,
            corner_radius=10,
            fg_color="#eef0f6",
            hover_color="#e2e6f2",
            text_color="#1a1d29",
            font=(FONT_FAMILY, 11, "bold"),
        ).grid(row=0, column=1, padx=(8, 0))


class StatusPill(ctk.CTkLabel):
    def __init__(self, parent):
        super().__init__(
            parent,
            text="",
            corner_radius=999,
            height=32,
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="transparent",
        )

    def success(self, text):
        self.configure(text=f"  ✓  {text}  ", fg_color="#e7f8f0", text_color=SUCCESS)

    def error(self, text):
        self.configure(text=f"  ✕  {text}  ", fg_color="#fdecec", text_color=DANGER)

    def clear(self):
        self.configure(text="", fg_color="transparent")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Conversor PDF ⇄ Imagem")
        self.geometry("920x600")
        self.minsize(860, 560)
        self.configure(fg_color="#eef0f6")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        self.pages = {}
        self._build_pdf_to_img_page()
        self._build_img_to_pdf_page()

        self._select_page("pdf2img")

    # ---------------- Sidebar ----------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=SIDEBAR_BG)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(28, 24))

        ctk.CTkLabel(
            brand,
            text="📄",
            width=44,
            height=44,
            corner_radius=12,
            fg_color=ACCENT,
            font=(FONT_FAMILY, 18),
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand,
            text="Conversor PDF",
            font=(FONT_FAMILY, 15, "bold"),
            text_color="#ffffff",
            anchor="w",
        ).pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(
            brand,
            text="Studio de conversão",
            font=(FONT_FAMILY, 10),
            text_color=SIDEBAR_TEXT,
            anchor="w",
        ).pack(fill="x")

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="x", padx=14)

        self.nav_buttons = {}
        for key, icon, label in (
            ("pdf2img", "📄", "PDF → Imagem"),
            ("img2pdf", "🖼", "Imagem → PDF"),
        ):
            btn = ctk.CTkButton(
                nav,
                text=f"  {icon}   {label}",
                anchor="w",
                height=44,
                corner_radius=10,
                font=(FONT_FAMILY, 12, "bold"),
                fg_color="transparent",
                hover_color="#242a3d",
                text_color=SIDEBAR_TEXT,
                command=lambda k=key: self._select_page(k),
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[key] = btn

        ctk.CTkLabel(
            sidebar,
            text="v1.0",
            font=(FONT_FAMILY, 9),
            text_color="#4a5068",
        ).pack(side="bottom", pady=16)

    def _select_page(self, key):
        for page_key, btn in self.nav_buttons.items():
            active = page_key == key
            btn.configure(
                fg_color=ACCENT if active else "transparent",
                text_color="#ffffff" if active else SIDEBAR_TEXT,
            )
        for page_key, page in self.pages.items():
            if page_key == key:
                page["title"].configure(text=page["title_text"])
                page["subtitle"].configure(text=page["subtitle_text"])
                page["frame"].tkraise()

    # ---------------- Content shell ----------------
    def _build_content_area(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=32, pady=28)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        self.page_title = ctk.CTkLabel(
            content, text="", font=(FONT_FAMILY, 20, "bold"), text_color="#1a1d29", anchor="w"
        )
        self.page_title.grid(row=0, column=0, sticky="ew")

        self.page_subtitle = ctk.CTkLabel(
            content, text="", font=(FONT_FAMILY, 12), text_color=MUTED, anchor="w"
        )
        self.page_subtitle.grid(row=1, column=0, sticky="ew", pady=(2, 18))

        self.pages_container = ctk.CTkFrame(content, fg_color="transparent")
        self.pages_container.grid(row=2, column=0, sticky="nsew")
        self.pages_container.grid_columnconfigure(0, weight=1)
        self.pages_container.grid_rowconfigure(0, weight=1)

    def _make_card(self):
        card = ctk.CTkFrame(
            self.pages_container,
            corner_radius=16,
            fg_color="#ffffff",
            border_width=1,
            border_color=CARD_BORDER,
        )
        card.grid(row=0, column=0, sticky="nsew")
        return card

    def _register_page(self, key, frame, title_text, subtitle_text):
        self.pages[key] = {
            "frame": frame,
            "title": self.page_title,
            "subtitle": self.page_subtitle,
            "title_text": title_text,
            "subtitle_text": subtitle_text,
        }

    # ---------------- PDF -> Imagem ----------------
    def _build_pdf_to_img_page(self):
        card = self._make_card()
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=26)

        FieldLabel(inner, "Arquivo PDF").pack(fill="x", pady=(0, 8))
        self.pdf_path_var = ctk.StringVar()
        PathField(inner, self.pdf_path_var, "Procurar...", self._select_pdf_file).pack(
            fill="x", pady=(0, 22)
        )

        FieldLabel(inner, "Formato de saída").pack(fill="x", pady=(0, 8))
        self.output_format_var = ctk.StringVar(value="png")
        format_row = ctk.CTkFrame(inner, fg_color="transparent")
        format_row.pack(fill="x", pady=(0, 22))
        ctk.CTkSegmentedButton(
            format_row,
            values=["PNG", "JPG"],
            variable=self._format_display_var(),
            command=self._on_format_change,
            font=(FONT_FAMILY, 11, "bold"),
            height=38,
            corner_radius=10,
            fg_color="#ffffff",
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color="#eef0f6",
            unselected_hover_color="#e2e6f2",
            text_color="#1a1d29",
            text_color_disabled="#1a1d29",
            width=220,
        ).pack(anchor="w")

        FieldLabel(inner, "Pasta de destino").pack(fill="x", pady=(0, 8))
        self.output_dir_var = ctk.StringVar()
        PathField(inner, self.output_dir_var, "Procurar...", self._select_output_dir).pack(
            fill="x", pady=(0, 30)
        )

        ctk.CTkButton(
            inner,
            text="Converter PDF para Imagem",
            command=self._convert_pdf_to_image,
            height=46,
            corner_radius=10,
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
        ).pack(fill="x")

        self.pdf_status = StatusPill(inner)
        self.pdf_status.pack(anchor="w", pady=(16, 0))

        self._register_page(
            "pdf2img",
            card,
            "PDF para Imagem",
            "Converta páginas de um PDF em arquivos PNG ou JPG",
        )

    def _format_display_var(self):
        self._format_display = ctk.StringVar(value="PNG")
        return self._format_display

    def _on_format_change(self, value):
        self.output_format_var.set(value.lower())

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
            self.pdf_status.success(f"{len(saved_files)} imagem(ns) gerada(s) com sucesso!")
            messagebox.showinfo(
                "Sucesso", f"{len(saved_files)} imagem(ns) salva(s) em:\n{output_dir}"
            )
        except Exception as exc:
            self.pdf_status.error("Falha ao converter")
            messagebox.showerror("Erro", f"Falha ao converter PDF:\n{exc}")

    # ---------------- Imagem -> PDF ----------------
    def _build_img_to_pdf_page(self):
        card = self._make_card()
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=26)

        list_header = ctk.CTkFrame(inner, fg_color="transparent")
        list_header.pack(fill="x", pady=(0, 8))
        FieldLabel(list_header, "Imagens selecionadas").pack(side="left")
        self.image_count_label = ctk.CTkLabel(
            list_header, text="0", font=(FONT_FAMILY, 10, "bold"), text_color=ACCENT
        )
        self.image_count_label.pack(side="left", padx=(6, 0))

        list_frame = ctk.CTkFrame(
            inner, corner_radius=10, fg_color="#f8f9fc", border_width=1, border_color=CARD_BORDER
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.image_paths = []
        self.images_listbox = ctk.CTkTextbox(
            list_frame,
            fg_color="transparent",
            text_color="#1a1d29",
            font=(FONT_FAMILY, 11),
            wrap="none",
            activate_scrollbars=True,
        )
        self.images_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self.images_listbox.configure(state="disabled")

        buttons_row = ctk.CTkFrame(inner, fg_color="transparent")
        buttons_row.pack(fill="x", pady=(0, 22))
        ctk.CTkButton(
            buttons_row,
            text="Adicionar imagens...",
            command=self._select_images,
            height=38,
            corner_radius=10,
            fg_color="#eef0f6",
            hover_color="#e2e6f2",
            text_color="#1a1d29",
            font=(FONT_FAMILY, 11, "bold"),
        ).pack(side="left")
        ctk.CTkButton(
            buttons_row,
            text="Limpar lista",
            command=self._clear_images,
            height=38,
            corner_radius=10,
            fg_color="#eef0f6",
            hover_color="#e2e6f2",
            text_color="#1a1d29",
            font=(FONT_FAMILY, 11, "bold"),
        ).pack(side="left", padx=(8, 0))

        FieldLabel(inner, "Arquivo PDF de saída").pack(fill="x", pady=(0, 8))
        self.output_pdf_var = ctk.StringVar()
        PathField(inner, self.output_pdf_var, "Salvar como...", self._select_output_pdf).pack(
            fill="x", pady=(0, 22)
        )

        ctk.CTkButton(
            inner,
            text="Converter Imagens para PDF",
            command=self._convert_images_to_pdf,
            height=46,
            corner_radius=10,
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
        ).pack(fill="x")

        self.img_status = StatusPill(inner)
        self.img_status.pack(anchor="w", pady=(16, 0))

        self._register_page(
            "img2pdf",
            card,
            "Imagem para PDF",
            "Combine imagens em um único arquivo PDF",
        )

    def _refresh_images_listbox(self):
        self.images_listbox.configure(state="normal")
        self.images_listbox.delete("1.0", "end")
        for path in self.image_paths:
            self.images_listbox.insert("end", f"🖼  {os.path.basename(path)}\n")
        self.images_listbox.configure(state="disabled")
        self.image_count_label.configure(text=str(len(self.image_paths)))

    def _select_images(self):
        paths = filedialog.askopenfilenames(
            title="Selecione as imagens",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")],
        )
        changed = False
        for path in paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                changed = True
        if changed:
            self._refresh_images_listbox()

    def _clear_images(self):
        self.image_paths = []
        self._refresh_images_listbox()

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
            self.img_status.success("PDF gerado com sucesso!")
            messagebox.showinfo("Sucesso", f"PDF salvo em:\n{output_pdf_path}")
        except Exception as exc:
            self.img_status.error("Falha ao converter")
            messagebox.showerror("Erro", f"Falha ao converter imagens:\n{exc}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
