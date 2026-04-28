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
    """Diálogo de exportação com seleção de formato e opção de divisão."""

    def __init__(
        self,
        parent: tk.Widget,
        on_export: Callable[[str, Path], None] | None = None,
        total_chars: int = 0,
    ) -> None:
        self.parent = parent
        self.on_export = on_export
        self.total_chars = total_chars
        # Resultado: (formato, caminho, max_chars_divisão_ou_None)
        self.result: tuple[str, Path, int | None] | None = None

    def show(self) -> tuple[str, Path, int | None] | None:
        """Exibe o diálogo e retorna (formato, caminho, split_chars) ou None."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Exportar Resultado")
        dialog.geometry("460x340")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - 460) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - 340) // 2
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

        # ── Divisão de Texto ──
        split_var = tk.BooleanVar(value=False)
        split_check = ttk.Checkbutton(
            main, text="✂️ Dividir em múltiplos arquivos",
            variable=split_var, command=lambda: _toggle_split(),
        )
        split_check.pack(anchor=tk.W)

        split_frame = ttk.Frame(main)
        split_frame.pack(fill=tk.X, padx=20, pady=(4, 0))

        ttk.Label(split_frame, text="Máximo de caracteres por arquivo:").pack(side=tk.LEFT)

        chars_var = tk.StringVar(value="5000")
        chars_entry = ttk.Entry(split_frame, textvariable=chars_var, width=8)
        chars_entry.pack(side=tk.LEFT, padx=6)
        chars_entry.configure(state=tk.DISABLED)

        # Info do texto
        if self.total_chars > 0:
            ttk.Label(
                main,
                text=f"   Texto total: {self.total_chars:,} caracteres",
                foreground="#888888",
                font=("Segoe UI", 9),
            ).pack(anchor=tk.W, padx=15, pady=(2, 0))

        def _toggle_split():
            if split_var.get():
                chars_entry.configure(state=tk.NORMAL)
            else:
                chars_entry.configure(state=tk.DISABLED)

        ttk.Separator(main).pack(fill=tk.X, pady=10)

        # ── Botões ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        def do_export():
            fmt = format_var.get()
            split_max = None

            if split_var.get():
                try:
                    split_max = int(chars_var.get())
                    if split_max < 100:
                        messagebox.showwarning(
                            "Aviso", "O mínimo é 100 caracteres por arquivo.",
                            parent=dialog,
                        )
                        return
                except ValueError:
                    messagebox.showerror(
                        "Erro", "Informe um número válido de caracteres.",
                        parent=dialog,
                    )
                    return

                # Para divisão, pedir diretório de saída
                dirpath = filedialog.askdirectory(
                    parent=dialog,
                    title="Selecione a pasta para salvar os arquivos",
                )
                if dirpath:
                    self.result = (fmt, Path(dirpath), split_max)
                    dialog.destroy()
            else:
                # Exportação normal, pedir arquivo
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
                    self.result = (fmt, Path(filepath), None)
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


class AIConfigDialog:
    """
    Diálogo de Configuração e Correção por IA.

    Permite ao usuário escolher provider (Ollama/Gemini),
    configurar modelo, testar conexão e corrigir o texto.
    """

    def __init__(self, parent: tk.Widget, text: str, app) -> None:
        self.parent = parent
        self.text = text
        self.app = app
        self.corrected_text: str | None = None
        self._is_correcting = False

    def show(self) -> str | None:
        """Exibe o diálogo e retorna o texto corrigido ou None."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🤖 Correção por IA")
        self.dialog.geometry("560x520")
        self.dialog.minsize(500, 460)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Centralizar
        self.dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - 560) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - 520) // 2
        self.dialog.geometry(f"+{x}+{y}")

        main = ttk.Frame(self.dialog, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # ── Provider ──
        provider_frame = ttk.LabelFrame(main, text="Provider de IA", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 10))

        self.provider_var = tk.StringVar(value=self.app.settings.ai_provider)

        radio_row = ttk.Frame(provider_frame)
        radio_row.pack(fill=tk.X)

        ttk.Radiobutton(
            radio_row, text="🦙 Ollama (Local)",
            variable=self.provider_var, value="ollama",
            command=self._on_provider_change,
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            radio_row, text="✨ Gemini (Cloud)",
            variable=self.provider_var, value="gemini",
            command=self._on_provider_change,
        ).pack(side=tk.LEFT)

        # ── Configuração do Ollama ──
        self.ollama_frame = ttk.Frame(provider_frame)
        self.ollama_frame.pack(fill=tk.X, pady=(8, 0))

        row1 = ttk.Frame(self.ollama_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="URL:", width=10).pack(side=tk.LEFT)
        self.ollama_url_var = tk.StringVar(value=self.app.settings.ollama_url)
        ttk.Entry(row1, textvariable=self.ollama_url_var, width=35).pack(side=tk.LEFT, padx=4)

        row2 = ttk.Frame(self.ollama_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Modelo:", width=10).pack(side=tk.LEFT)
        self.ollama_model_var = tk.StringVar(value=self.app.settings.ollama_model)
        self.ollama_model_entry = ttk.Combobox(
            row2, textvariable=self.ollama_model_var, width=32,
            values=["llama3.2", "llama3.1", "mistral", "gemma2", "qwen2.5", "phi3"],
        )
        self.ollama_model_entry.pack(side=tk.LEFT, padx=4)

        # ── Configuração do Gemini ──
        self.gemini_frame = ttk.Frame(provider_frame)

        grow1 = ttk.Frame(self.gemini_frame)
        grow1.pack(fill=tk.X, pady=2)
        ttk.Label(grow1, text="API Key:", width=10).pack(side=tk.LEFT)
        self.gemini_key_var = tk.StringVar(value=self.app.settings.gemini_api_key)
        ttk.Entry(grow1, textvariable=self.gemini_key_var, width=35, show="•").pack(side=tk.LEFT, padx=4)

        grow2 = ttk.Frame(self.gemini_frame)
        grow2.pack(fill=tk.X, pady=2)
        ttk.Label(grow2, text="Modelo:", width=10).pack(side=tk.LEFT)
        self.gemini_model_var = tk.StringVar(value=self.app.settings.gemini_model)
        ttk.Combobox(
            grow2, textvariable=self.gemini_model_var, width=32,
            values=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
            state="readonly",
        ).pack(side=tk.LEFT, padx=4)

        # ── Botão de Teste ──
        test_row = ttk.Frame(provider_frame)
        test_row.pack(fill=tk.X, pady=(8, 0))

        self.btn_test = ttk.Button(
            test_row, text="🔌 Testar Conexão", command=self._test_connection,
            width=18,
        )
        self.btn_test.pack(side=tk.LEFT)

        self.test_label = ttk.Label(test_row, text="", font=("Segoe UI", 9))
        self.test_label.pack(side=tk.LEFT, padx=8)

        # ── Info do Texto ──
        ttk.Separator(main).pack(fill=tk.X, pady=8)

        info_frame = ttk.Frame(main)
        info_frame.pack(fill=tk.X)

        total_chars = len(self.text)
        total_words = len(self.text.split())
        ttk.Label(
            info_frame,
            text=f"📝 Texto: {total_chars:,} caracteres  •  {total_words:,} palavras",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT)

        # ── Progresso ──
        progress_frame = ttk.Frame(main)
        progress_frame.pack(fill=tk.X, pady=(8, 0))

        self.progress = ttk.Progressbar(progress_frame, mode="determinate", length=350)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress_label = ttk.Label(
            progress_frame, text="", font=("Segoe UI", 9), width=20,
        )
        self.progress_label.pack(side=tk.LEFT, padx=(8, 0))

        # ── Resultado ──
        result_frame = ttk.LabelFrame(main, text="Resultado", padding=8)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_text = tk.Text(
            result_frame,
            wrap=tk.WORD,
            font=("Cascadia Code", 10),
            background="#1e1e2e",
            foreground="#cdd6f4",
            border=0,
            padx=8, pady=4,
            height=8,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.configure(command=self.result_text.yview)

        # ── Botões ──
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X)

        self.btn_apply = ttk.Button(
            btn_frame, text="✅ Aplicar Correção",
            command=self._apply_correction,
            style="success.TButton",
            state=tk.DISABLED,
        )
        self.btn_apply.pack(side=tk.RIGHT, padx=(5, 0))

        self.btn_correct = ttk.Button(
            btn_frame, text="🤖 Corrigir Texto",
            command=self._start_correction,
            style="info.TButton",
        )
        self.btn_correct.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            btn_frame, text="Fechar", command=self._close,
        ).pack(side=tk.RIGHT)

        # Mostrar frame correto
        self._on_provider_change()

        self.dialog.wait_window()
        return self.corrected_text

    def _on_provider_change(self) -> None:
        """Alterna campos conforme o provider selecionado."""
        if self.provider_var.get() == "ollama":
            self.gemini_frame.pack_forget()
            self.ollama_frame.pack(fill=tk.X, pady=(8, 0))
        else:
            self.ollama_frame.pack_forget()
            self.gemini_frame.pack(fill=tk.X, pady=(8, 0))
        self.test_label.configure(text="")

    def _test_connection(self) -> None:
        """Testa a conexão com o provider selecionado."""
        self.test_label.configure(text="Testando...", foreground="#f9e2af")
        self.dialog.update()

        from voxtext.ai.providers import create_provider

        provider_name = self.provider_var.get()
        try:
            if provider_name == "ollama":
                provider = create_provider(
                    "ollama",
                    model=self.ollama_model_var.get(),
                    base_url=self.ollama_url_var.get(),
                )
            else:
                provider = create_provider(
                    "gemini",
                    model=self.gemini_model_var.get(),
                    api_key=self.gemini_key_var.get(),
                )

            success, msg = provider.test_connection()

            if success:
                self.test_label.configure(text=f"✅ {msg}", foreground="#a6e3a1")
                # Se Ollama, atualizar lista de modelos
                if provider_name == "ollama":
                    models = provider.list_models()
                    if models:
                        self.ollama_model_entry.configure(values=models)
            else:
                self.test_label.configure(text=f"❌ {msg}", foreground="#f38ba8")

        except Exception as e:
            self.test_label.configure(text=f"❌ {e}", foreground="#f38ba8")

    def _start_correction(self) -> None:
        """Inicia a correção em thread separada."""
        if self._is_correcting:
            return

        self._is_correcting = True
        self.btn_correct.configure(state=tk.DISABLED)
        self.btn_apply.configure(state=tk.DISABLED)
        self.progress["value"] = 0
        self.progress_label.configure(text="Iniciando...")

        import threading

        def run():
            try:
                provider_name = self.provider_var.get()
                if provider_name == "ollama":
                    model = self.ollama_model_var.get()
                    api_key = ""
                    base_url = self.ollama_url_var.get()
                else:
                    model = self.gemini_model_var.get()
                    api_key = self.gemini_key_var.get()
                    base_url = ""

                result = self.app.correct_with_ai(
                    text=self.text,
                    provider_name=provider_name,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    on_progress=self._update_progress,
                )

                self.dialog.after(0, lambda: self._on_correction_done(result))

            except Exception as e:
                self.dialog.after(0, lambda: self._on_correction_error(str(e)))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _update_progress(self, current: int, total: int) -> None:
        """Thread-safe progress update."""
        if total > 0:
            pct = int((current / total) * 100)
            self.dialog.after(0, lambda: self._set_progress(pct, f"Chunk {current}/{total}"))

    def _set_progress(self, value: int, label: str) -> None:
        self.progress["value"] = value
        self.progress_label.configure(text=label)

    def _on_correction_done(self, result) -> None:
        """Callback quando correção termina."""
        self._is_correcting = False
        self.btn_correct.configure(state=tk.NORMAL)

        if not result.success:
            self.progress_label.configure(text="❌ Erro")
            messagebox.showerror(
                "Erro na Correção",
                f"Provider: {result.provider}\n\n{result.error}",
                parent=self.dialog,
            )
            return

        self.progress["value"] = 100
        self.progress_label.configure(
            text=f"✅ {result.chunks_processed} chunk(s) • {result.total_tokens} tokens"
        )

        # Exibir resultado
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", result.corrected_text)
        self.result_text.configure(state=tk.DISABLED)

        self.corrected_text = result.corrected_text
        self.btn_apply.configure(state=tk.NORMAL)

    def _on_correction_error(self, error: str) -> None:
        self._is_correcting = False
        self.btn_correct.configure(state=tk.NORMAL)
        self.progress_label.configure(text="❌ Erro")
        messagebox.showerror("Erro", error, parent=self.dialog)

    def _apply_correction(self) -> None:
        """Aplica a correção e fecha o diálogo."""
        self.dialog.destroy()

    def _close(self) -> None:
        """Fecha sem aplicar."""
        self.corrected_text = None
        self.dialog.destroy()
