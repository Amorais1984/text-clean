"""
Janela principal do VoxText Engine.

Layout split-view com texto original à esquerda e texto processado
à direita, barra de ferramentas no topo e barra de status inferior.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from voxtext.app import VoxTextApp

from voxtext.gui.toolbar import Toolbar
from voxtext.gui.editor_panel import EditorPanel
from voxtext.gui.dialogs import ExportDialog, AboutDialog, SplitDialog


class MainWindow:
    """Janela principal da aplicação VoxText Engine."""

    def __init__(self, app: VoxTextApp) -> None:
        self.app = app
        self._current_file: Path | None = None
        self._build_window()

    def _build_window(self) -> None:
        try:
            import ttkbootstrap as ttkb
            self.root = ttkb.Window(
                title="VoxText Engine — Otimizador de Texto para TTS",
                themename="darkly",
                size=(1280, 780),
                minsize=(900, 600),
            )
        except ImportError:
            self.root = tk.Tk()
            self.root.title("VoxText Engine — Otimizador de Texto para TTS")
            self.root.geometry("1280x780")
            self.root.minsize(900, 600)
            # Tema escuro manual
            style = ttk.Style()
            style.theme_use("clam")
            self.root.configure(bg="#1e1e2e")

        # ── Menu ──
        self._build_menu()

        # ── Toolbar ──
        self.toolbar = Toolbar(
            self.root,
            on_import=self._on_import,
            on_process=self._on_process,
            on_export=self._on_export,
            on_split=self._on_split,
            on_mode_change=self._on_mode_change,
        )
        self.toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))

        # ── Separador ──
        ttk.Separator(self.root).pack(fill=tk.X, padx=5, pady=5)

        # ── Split View: Painéis de Texto ──
        panes = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Painel esquerdo: Texto Original
        self.original_panel = EditorPanel(
            panes, title="📄 Texto Original", editable=False,
        )
        panes.add(self.original_panel, weight=1)

        # Painel direito: Texto Processado
        self.processed_panel = EditorPanel(
            panes, title="✨ Texto Processado", editable=True,
        )
        panes.add(self.processed_panel, weight=1)

        # ── Status Bar ──
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.status_text = ttk.Label(
            self.status_bar,
            text="Nenhum arquivo carregado",
            font=("Segoe UI", 9),
        )
        self.status_text.pack(side=tk.LEFT)

        self.stats_text = ttk.Label(
            self.status_bar,
            text="",
            font=("Segoe UI", 9),
            foreground="#888888",
        )
        self.stats_text.pack(side=tk.RIGHT)

        # ── Atalhos de teclado ──
        self.root.bind("<Control-o>", lambda e: self._on_import())
        self.root.bind("<Control-s>", lambda e: self._on_export())
        self.root.bind("<Control-d>", lambda e: self._on_split())
        self.root.bind("<F5>", lambda e: self._on_process())

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Importar (Ctrl+O)", command=self._on_import)
        file_menu.add_command(label="Exportar (Ctrl+S)", command=self._on_export)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # Menu Processar
        proc_menu = tk.Menu(menubar, tearoff=0)
        proc_menu.add_command(label="Processar (F5)", command=self._on_process)
        proc_menu.add_separator()
        proc_menu.add_command(label="Dividir Texto (Ctrl+D)", command=self._on_split)
        menubar.add_cascade(label="Processar", menu=proc_menu)

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="Sobre", command=lambda: AboutDialog.show(self.root)
        )
        menubar.add_cascade(label="Ajuda", menu=help_menu)

        self.root.configure(menu=menubar)

    # ── Callbacks ────────────────────────────────────────────

    def _on_import(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Importar Arquivo",
            filetypes=[
                ("Arquivos suportados", "*.pdf *.txt"),
                ("PDF", "*.pdf"),
                ("Texto", "*.txt"),
                ("Todos", "*.*"),
            ],
        )
        if not filepath:
            return

        self._current_file = Path(filepath)
        self.status_text.configure(text=f"Arquivo: {self._current_file.name}")

        # Carregar texto original via parser
        try:
            raw_text = self.app.load_file(self._current_file)
            self.original_panel.set_text(raw_text)
            self.processed_panel.set_text("")
            self.toolbar.enable_export(False)
        except Exception as e:
            messagebox.showerror("Erro ao Importar", str(e), parent=self.root)

    def _on_process(self) -> None:
        if not self._current_file:
            messagebox.showwarning(
                "Aviso", "Importe um arquivo primeiro.", parent=self.root
            )
            return

        self.toolbar.set_processing(True)
        self.toolbar.set_progress(0, "Processando...")

        def run_pipeline():
            try:
                result = self.app.process_file(
                    self._current_file,
                    on_progress=self._update_progress_safe,
                )
                # Atualizar GUI na thread principal
                self.root.after(0, lambda: self._on_processing_done(result))
            except Exception as e:
                self.root.after(0, lambda: self._on_processing_error(str(e)))

        thread = threading.Thread(target=run_pipeline, daemon=True)
        thread.start()

    def _update_progress_safe(self, stage_name: str, progress: float) -> None:
        """Thread-safe progress update."""
        self.root.after(0, lambda: self.toolbar.set_progress(progress, stage_name))

    def _on_processing_done(self, result) -> None:
        self.toolbar.set_processing(False)
        self.toolbar.set_progress(100, "Concluído ✓")
        self.toolbar.enable_export(True)

        # Exibir texto processado
        self.processed_panel.set_text(result.processed_text)

        # Atualizar estatísticas
        stats = result.stats
        self.stats_text.configure(
            text=(
                f"⏱ {stats.processing_time_seconds:.2f}s  •  "
                f"📊 {stats.segment_count} segmentos  •  "
                f"📝 {stats.original_char_count:,} → {stats.processed_char_count:,} chars"
            )
        )

        if result.errors:
            messagebox.showwarning(
                "Avisos",
                f"Processamento concluído com {len(result.errors)} aviso(s):\n\n"
                + "\n".join(result.errors[:5]),
                parent=self.root,
            )

    def _on_processing_error(self, error: str) -> None:
        self.toolbar.set_processing(False)
        self.toolbar.set_progress(0, "Erro")
        messagebox.showerror("Erro no Processamento", error, parent=self.root)

    def _on_export(self) -> None:
        if not self.app.last_result:
            messagebox.showwarning(
                "Aviso", "Processe um arquivo primeiro.", parent=self.root
            )
            return

        dialog = ExportDialog(self.root, on_export=None)
        result = dialog.show()

        if result:
            fmt, path = result
            try:
                exported = self.app.export_result(fmt, path)
                messagebox.showinfo(
                    "Exportado",
                    f"Arquivo exportado com sucesso:\n{exported}",
                    parent=self.root,
                )
            except Exception as e:
                messagebox.showerror("Erro ao Exportar", str(e), parent=self.root)

    def _on_mode_change(self, mode_name: str) -> None:
        mode_map = {
            "Acadêmico": "academic",
            "Natural": "natural",
            "Compacto": "compact",
        }
        mode_key = mode_map.get(mode_name, "natural")
        self.app.set_processing_mode(mode_key)
        self.status_text.configure(
            text=f"Modo: {mode_name}"
            + (f"  |  Arquivo: {self._current_file.name}" if self._current_file else "")
        )

    def _on_split(self) -> None:
        """Abre o diálogo de divisão de texto."""
        # Pegar texto do painel processado (ou original se não processou)
        text = self.processed_panel.get_text()
        if not text.strip():
            text = self.original_panel.get_text()
        if not text.strip():
            messagebox.showwarning(
                "Aviso", "Importe e processe um arquivo primeiro.",
                parent=self.root,
            )
            return

        dialog = SplitDialog(self.root, text, self.app)
        dialog.show()

    def run(self) -> None:
        """Inicia o loop principal da interface."""
        self.root.mainloop()
