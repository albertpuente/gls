#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import sys
from datetime import datetime
from pathlib import Path
from stat import filemode

from rich.syntax import Syntax
from rich.text import Text
from rich.traceback import Traceback
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import var
from textual.widgets import Button, DirectoryTree, Footer, Header, Static


def sizeof_fmt(num, suffix='B'):
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)
    if magnitude > 7:
        return '{:.1f}{}{}'.format(val, 'Yi', suffix)
    return '{:3.1f}{}{}'.format(val, ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi'][magnitude], suffix)


class GLS(App):
    """Textual code browser app."""

    CSS_PATH = "browser.css"
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        # ("d", "toggle_dark", "Toggle Dark Mode"),
        # ("e", "edit", "Edit"),
        # ("d", "delete", "Delete"),
        ("q", "quit", "Quit"),
    ]

    show_tree = var(True)

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header(show_clock=True)
        yield Container(
            DirectoryTree(path, id="tree-view"),
            Vertical(Static(id="code", expand=True), id="code-view"),
            Horizontal(
                Static(
                    id="info",
                    expand=True,
                    renderable=Text.assemble(
                        ("Select a file to see its contents", "bold #0078D4"))
                ),
                id="info-view"
            ),
        )
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        code_view = self.query_one("#code", Static)
        try:
            syntax = Syntax.from_path(
                event.path,
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                # theme="github-dark",
            )
        except Exception:
            # code_view.update(Traceback(theme="github-dark", width=None))
            code_view.update("Cannot display this file")
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#code-view").scroll_home(animate=False)
            self.sub_title = event.path

        # Info view
        status = Path(event.path).stat()
        info_view = self.query_one("#info", Static)
        mod_date = datetime.utcfromtimestamp(
            status.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        label_style = "bold #0078D4"
        info_view.update(
            Text.assemble(
                ("Size: ", label_style),
                f"{sizeof_fmt(status.st_size)} ",
                ("Perms: ", label_style),
                f"{filemode(status.st_mode)} ",
                ("Modified: ", label_style),
                f"{mod_date}"
            )
        )

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

    # def action_toggle_dark(self) -> None:
    #     """An action to toggle dark mode."""
    #     self.dark = not self.dark


if __name__ == "__main__":
    GLS().run()
