"""
Barra de ferramentas da interface VoxText.

Contém botões de importação, processamento, exportação,
seleção de modo e indicador de progresso.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


class Toolbar(ttk.Frame):
    """Barra de ferramentas principal."""

    def __init__(
        self,
        parent: tk.Widget,
        on_import: Callable[[], None],
        on_process: Callable[[], None],
        on_export: Callable[[], None],
        on_split: Callable[[], None],
        on_ai_correct: Callable[[], None],
        on_mode_change: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)

        self._on_import = on_import
        self._on_process = on_process
        self._on_export = on_export
        self._on_split = on_split
        self._on_ai_correct = on_ai_correct
        self._on_mode_change = on_mode_change

        self._build_ui()

    def _build_ui(self) -> None:
        # Container com padding
        self.configure(padding=(10, 5))

        # ── Botão Importar ──
        self.btn_import = ttk.Button(
            self, text="📂 Importar", command=self._on_import,
            style="info.TButton", width=14,
        )
        self.btn_import.pack(side=tk.LEFT, padx=(0, 5))

        # ── Separador ──
        ttk.Separator(self, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8, pady=2
        )

        # ── Modo de Otimização ──
        mode_frame = ttk.Frame(self)
        mode_frame.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(mode_frame, text="Modo:").pack(side=tk.LEFT, padx=(0, 4))

        self.mode_var = tk.StringVar(value="Natural")
        self.mode_combo = ttk.Combobox(
            mode_frame, textvariable=self.mode_var,
            values=["Acadêmico", "Natural", "Compacto"],
            state="readonly", width=12,
        )
        self.mode_combo.pack(side=tk.LEFT)
        self.mode_combo.bind("<<ComboboxSelected>>", self._mode_changed)

        # ── Separador ──
        ttk.Separator(self, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8, pady=2
        )

        # ── Botão Processar ──
        self.btn_process = ttk.Button(
            self, text="⚡ Processar", command=self._on_process,
            style="success.TButton", width=14,
        )
        self.btn_process.pack(side=tk.LEFT, padx=(0, 5))

        # ── Botão Exportar ──
        self.btn_export = ttk.Button(
            self, text="💾 Exportar", command=self._on_export,
            style="warning.TButton", width=14, state=tk.DISABLED,
        )
        self.btn_export.pack(side=tk.LEFT, padx=(0, 5))

        # ── Separador ──
        ttk.Separator(self, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8, pady=2
        )

        # ── Botão Dividir ──
        self.btn_split = ttk.Button(
            self, text="✂️ Dividir", command=self._on_split,
            style="info.TButton", width=14, state=tk.DISABLED,
        )
        self.btn_split.pack(side=tk.LEFT, padx=(0, 5))

        # ── Botão IA Corrigir ──
        self.btn_ai = ttk.Button(
            self, text="🤖 IA", command=self._on_ai_correct,
            style="danger.TButton", width=10, state=tk.DISABLED,
        )
        self.btn_ai.pack(side=tk.LEFT, padx=(0, 5))

        # ── Barra de Progresso ──
        self.progress = ttk.Progressbar(
            self, mode="determinate", length=200,
        )
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))

        # ── Label de status ──
        self.status_label = ttk.Label(self, text="Pronto")
        self.status_label.pack(side=tk.RIGHT, padx=(5, 0))

    def _mode_changed(self, event=None) -> None:
        self._on_mode_change(self.mode_var.get())

    def set_progress(self, value: float, label: str = "") -> None:
        """Atualiza a barra de progresso (0-100)."""
        self.progress["value"] = value
        if label:
            self.status_label.configure(text=label)

    def set_processing(self, processing: bool) -> None:
        """Habilita/desabilita botões durante processamento."""
        state = tk.DISABLED if processing else tk.NORMAL
        self.btn_import.configure(state=state)
        self.btn_process.configure(state=state)
        self.mode_combo.configure(state="disabled" if processing else "readonly")

    def enable_export(self, enabled: bool = True) -> None:
        """Habilita/desabilita botão de exportação, divisão e IA."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.btn_export.configure(state=state)
        self.btn_split.configure(state=state)
        self.btn_ai.configure(state=state)
