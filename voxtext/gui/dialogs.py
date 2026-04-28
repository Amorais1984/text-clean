"""
Diálogos auxiliares da interface VoxText.

Inclui diálogos de exportação e configuração avançada.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Callable


class ExportDialog:
    """Diálogo de exportação com seleção de formato e caminho."""

    def __init__(
        self,
        parent: tk.Widget,
        on_export: Callable[[str, Path], None],
    ) -> None:
        self.parent = parent
        self.on_export = on_export
        self.result: tuple[str, Path] | None = None

    def show(self) -> tuple[str, Path] | None:
        """Exibe o diálogo e retorna (formato, caminho) ou None."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Exportar Resultado")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - 420) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - 220) // 2
        dialog.geometry(f"+{x}+{y}")

        main = ttk.Frame(dialog, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Formato ──
        ttk.Label(main, text="Formato de Exportação:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)

        format_var = tk.StringVar(value="txt")
        formats = [
            ("📄 Texto Limpo (.txt)", "txt"),
            ("📋 JSON Estruturado (.json)", "json"),
            ("🔊 SSML (.ssml)", "ssml"),
        ]
        for label, value in formats:
            ttk.Radiobutton(
                main, text=label, variable=format_var, value=value,
            ).pack(anchor=tk.W, padx=15, pady=2)

        ttk.Separator(main).pack(fill=tk.X, pady=10)

        # ── Botões ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        def do_export():
            fmt = format_var.get()
            ext_map = {"txt": ".txt", "json": ".json", "ssml": ".ssml"}
            filepath = filedialog.asksaveasfilename(
                parent=dialog,
                title="Salvar como",
                defaultextension=ext_map[fmt],
                filetypes=[
                    ("Texto", "*.txt"),
                    ("JSON", "*.json"),
                    ("SSML", "*.ssml"),
                    ("Todos", "*.*"),
                ],
            )
            if filepath:
                self.result = (fmt, Path(filepath))
                dialog.destroy()

        ttk.Button(
            btn_frame, text="Exportar", command=do_export,
            style="success.TButton",
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            btn_frame, text="Cancelar", command=dialog.destroy,
        ).pack(side=tk.RIGHT)

        dialog.wait_window()
        return self.result


class AboutDialog:
    """Diálogo Sobre o aplicativo."""

    @staticmethod
    def show(parent: tk.Widget) -> None:
        messagebox.showinfo(
            "Sobre VoxText Engine",
            "VoxText Engine v1.0.0\n\n"
            "Sistema de Organização de Texto para TTS\n\n"
            "Transforma textos brutos em versões otimizadas\n"
            "para síntese de fala.\n\n"
            "© 2026 VoxText Team",
            parent=parent,
        )


class SplitDialog:
    """
    Diálogo de Divisão de Texto.

    Permite ao usuário definir um limite de caracteres por parte,
    visualizar as partes resultantes e exportar cada uma individualmente.
    """

    def __init__(self, parent: tk.Widget, text: str, app) -> None:
        self.parent = parent
        self.text = text
        self.app = app
        self.chunks = []
        self._current_chunk_idx = 0

    def show(self) -> None:
        """Exibe o diálogo de divisão de texto."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("✂️ Divisor de Texto")
        self.dialog.geometry("750x580")
        self.dialog.minsize(650, 500)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Centralizar
        self.dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - 750) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - 580) // 2
        self.dialog.geometry(f"+{x}+{y}")

        main = ttk.Frame(self.dialog, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Configuração ──
        config_frame = ttk.LabelFrame(main, text="Configuração", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))

        row = ttk.Frame(config_frame)
        row.pack(fill=tk.X)

        ttk.Label(row, text="Máximo de caracteres por parte:").pack(side=tk.LEFT)

        self.chars_var = tk.StringVar(value="5000")
        self.chars_entry = ttk.Entry(row, textvariable=self.chars_var, width=10)
        self.chars_entry.pack(side=tk.LEFT, padx=8)

        self.btn_split = ttk.Button(
            row, text="✂️ Dividir", command=self._do_split,
            style="success.TButton", width=12,
        )
        self.btn_split.pack(side=tk.LEFT, padx=(5, 0))

        # Info do texto original
        total_chars = len(self.text)
        total_words = len(self.text.split())
        ttk.Label(
            config_frame,
            text=f"Texto original: {total_chars:,} caracteres  •  {total_words:,} palavras",
            foreground="#888888",
        ).pack(anchor=tk.W, pady=(5, 0))

        # ── Resultado da divisão ──
        result_frame = ttk.LabelFrame(main, text="Resultado", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Barra de info + navegação
        nav_frame = ttk.Frame(result_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 8))

        self.result_label = ttk.Label(
            nav_frame, text="Configure o limite e clique em Dividir.",
            font=("Segoe UI", 9),
        )
        self.result_label.pack(side=tk.LEFT)

        # Navegação entre partes
        self.btn_next = ttk.Button(
            nav_frame, text="▶", command=self._next_chunk, width=3, state=tk.DISABLED,
        )
        self.btn_next.pack(side=tk.RIGHT, padx=(2, 0))

        self.nav_label = ttk.Label(nav_frame, text="", font=("Segoe UI", 9, "bold"))
        self.nav_label.pack(side=tk.RIGHT, padx=8)

        self.btn_prev = ttk.Button(
            nav_frame, text="◀", command=self._prev_chunk, width=3, state=tk.DISABLED,
        )
        self.btn_prev.pack(side=tk.RIGHT, padx=(0, 2))

        # Área de preview do chunk
        preview_frame = ttk.Frame(result_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.preview_text = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            font=("Cascadia Code", 10),
            background="#1e1e2e",
            foreground="#cdd6f4",
            border=0,
            padx=8, pady=4,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set,
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.configure(command=self.preview_text.yview)

        # Info do chunk atual
        self.chunk_info = ttk.Label(
            result_frame, text="", font=("Segoe UI", 9), foreground="#888888",
        )
        self.chunk_info.pack(anchor=tk.W, pady=(5, 0))

        # ── Botões de ação ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        self.btn_export_all = ttk.Button(
            btn_frame, text="💾 Exportar Todas as Partes",
            command=self._export_all, style="warning.TButton",
            state=tk.DISABLED,
        )
        self.btn_export_all.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            btn_frame, text="Fechar", command=self.dialog.destroy,
        ).pack(side=tk.RIGHT)

        # Bind Enter na entry
        self.chars_entry.bind("<Return>", lambda e: self._do_split())

    def _do_split(self) -> None:
        """Executa a divisão do texto."""
        try:
            max_chars = int(self.chars_var.get())
        except ValueError:
            messagebox.showerror(
                "Erro", "Informe um número válido de caracteres.",
                parent=self.dialog,
            )
            return

        if max_chars < 100:
            messagebox.showwarning(
                "Aviso", "O mínimo recomendado é 100 caracteres por parte.",
                parent=self.dialog,
            )
            return

        self.chunks = self.app.split_text(self.text, max_chars)
        self._current_chunk_idx = 0

        if not self.chunks:
            self.result_label.configure(text="Nenhum texto para dividir.")
            return

        self.result_label.configure(
            text=f"Texto dividido em {len(self.chunks)} parte(s)"
        )

        # Habilitar navegação e export
        self.btn_export_all.configure(state=tk.NORMAL)
        if len(self.chunks) > 1:
            self.btn_next.configure(state=tk.NORMAL)

        self._show_chunk(0)

    def _show_chunk(self, idx: int) -> None:
        """Exibe o chunk no índice dado."""
        if not self.chunks or idx < 0 or idx >= len(self.chunks):
            return

        self._current_chunk_idx = idx
        chunk = self.chunks[idx]

        # Atualizar preview
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", chunk.text)
        self.preview_text.configure(state=tk.DISABLED)

        # Atualizar navegação
        self.nav_label.configure(text=f"Parte {idx + 1} / {len(self.chunks)}")
        self.btn_prev.configure(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        self.btn_next.configure(
            state=tk.NORMAL if idx < len(self.chunks) - 1 else tk.DISABLED
        )

        # Atualizar info
        self.chunk_info.configure(
            text=f"📝 {chunk.char_count:,} caracteres  •  {chunk.word_count:,} palavras"
        )

    def _prev_chunk(self) -> None:
        self._show_chunk(self._current_chunk_idx - 1)

    def _next_chunk(self) -> None:
        self._show_chunk(self._current_chunk_idx + 1)

    def _export_all(self) -> None:
        """Exporta todas as partes como arquivos individuais."""
        output_dir = filedialog.askdirectory(
            parent=self.dialog,
            title="Selecione a pasta para salvar as partes",
        )
        if not output_dir:
            return

        try:
            exported = self.app.export_chunks(self.chunks, Path(output_dir))
            messagebox.showinfo(
                "Exportado",
                f"{len(exported)} arquivo(s) exportado(s) em:\n{output_dir}\n\n"
                + "\n".join(f"  • {p.name}" for p in exported[:10])
                + ("\n  ..." if len(exported) > 10 else ""),
                parent=self.dialog,
            )
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", str(e), parent=self.dialog)

