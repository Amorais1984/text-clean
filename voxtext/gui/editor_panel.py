"""
Painel de edição de texto com funcionalidades avançadas.

Exibe texto com syntax highlighting para tags SSML,
numeração de linhas e suporte a edição manual.
"""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk


class EditorPanel(ttk.Frame):
    """Painel de texto com numeração de linhas e highlight de SSML."""

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "Texto",
        editable: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.title = title
        self.editable = editable
        self._build_ui()

    def _build_ui(self) -> None:
        # ── Header ──
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=5, pady=(5, 2))

        self.title_label = ttk.Label(
            header, text=self.title,
            font=("Segoe UI", 11, "bold"),
        )
        self.title_label.pack(side=tk.LEFT)

        self.stats_label = ttk.Label(
            header, text="",
            font=("Segoe UI", 9),
            foreground="#888888",
        )
        self.stats_label.pack(side=tk.RIGHT)

        # ── Área de texto com scrollbar ──
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Line numbers
        self.line_numbers = tk.Text(
            text_frame, width=4,
            padx=4, pady=4,
            takefocus=0,
            border=0,
            background="#1e1e2e",
            foreground="#585b70",
            state=tk.DISABLED,
            font=("Cascadia Code", 10),
            cursor="arrow",
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            padx=8, pady=4,
            font=("Cascadia Code", 10),
            background="#1e1e2e",
            foreground="#cdd6f4",
            insertbackground="#f5c2e7",
            selectbackground="#45475a",
            selectforeground="#cdd6f4",
            border=0,
            undo=True,
            maxundo=50,
            yscrollcommand=scrollbar.set,
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.configure(command=self._on_scroll)

        if not self.editable:
            self.text.configure(state=tk.DISABLED)

        # Bind events
        self.text.bind("<KeyRelease>", self._on_text_change)
        self.text.bind("<MouseWheel>", self._on_mousewheel)

        # Configurar tags de syntax highlighting
        self._configure_tags()

    def _configure_tags(self) -> None:
        """Configura tags de cores para SSML."""
        self.text.tag_configure("ssml_tag", foreground="#89b4fa")
        self.text.tag_configure("ssml_attr", foreground="#a6e3a1")
        self.text.tag_configure("ssml_value", foreground="#fab387")
        self.text.tag_configure("heading", foreground="#f5c2e7", font=("Cascadia Code", 10, "bold"))
        self.text.tag_configure("emphasis", foreground="#f9e2af")

    def set_text(self, content: str) -> None:
        """Define o conteúdo do editor."""
        was_disabled = self.text.cget("state") == tk.DISABLED
        if was_disabled:
            self.text.configure(state=tk.NORMAL)

        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)

        self._apply_highlighting()
        self._update_line_numbers()
        self._update_stats()

        if was_disabled:
            self.text.configure(state=tk.DISABLED)

    def get_text(self) -> str:
        """Retorna o conteúdo do editor."""
        return self.text.get("1.0", tk.END).rstrip("\n")

    def _apply_highlighting(self) -> None:
        """Aplica syntax highlighting para tags SSML."""
        content = self.text.get("1.0", tk.END)

        # Remover tags existentes
        for tag in ("ssml_tag", "ssml_attr", "ssml_value"):
            self.text.tag_remove(tag, "1.0", tk.END)

        # Highlight SSML tags
        for match in re.finditer(r"</?[\w]+[^>]*>", content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add("ssml_tag", start, end)

        # Highlight attribute values
        for match in re.finditer(r'"[^"]*"', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add("ssml_value", start, end)

    def _update_line_numbers(self) -> None:
        """Atualiza a numeração de linhas."""
        self.line_numbers.configure(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)

        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", numbers)

        self.line_numbers.configure(state=tk.DISABLED)

    def _update_stats(self) -> None:
        """Atualiza label de estatísticas."""
        content = self.get_text()
        chars = len(content)
        words = len(content.split())
        lines = content.count("\n") + 1
        self.stats_label.configure(
            text=f"{chars:,} chars  •  {words:,} words  •  {lines} lines"
        )

    def _on_text_change(self, event=None) -> None:
        self._update_line_numbers()
        self._update_stats()

    def _on_scroll(self, *args) -> None:
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def _on_mousewheel(self, event) -> None:
        self.line_numbers.yview_scroll(
            int(-1 * (event.delta / 120)), "units"
        )
