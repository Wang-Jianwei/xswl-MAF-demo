from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_framework import tool


@dataclass(slots=True)
class ToolingConfig:
    workspace_root: Path
    allowed_commands: set[str]
    command_timeout_seconds: int


def _normalize_command_name(command_name: str) -> str:
    normalized = Path(command_name).name.strip().lower()
    if normalized.endswith(".exe"):
        return normalized[:-4]
    return normalized


def _parse_allowed_commands(raw: str) -> set[str]:
    return {
        _normalize_command_name(item)
        for item in raw.split(",")
        if item.strip()
    }


def _safe_resolve(workspace_root: Path, relative_path: str) -> Path:
    root = workspace_root.resolve()
    target = (root / relative_path).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Path out of workspace is not allowed: {relative_path}")
    return target


def build_dev_tools(
    workspace_root: str,
    allowed_commands: str,
    command_timeout_seconds: int,
) -> list[Any]:
    config = ToolingConfig(
        workspace_root=Path(workspace_root),
        allowed_commands=_parse_allowed_commands(allowed_commands),
        command_timeout_seconds=command_timeout_seconds,
    )

    @tool(approval_mode="never_require")
    def read_file(relative_path: str, start_line: int = 1, end_line: int = 200) -> str:
        """读取工作区内文本文件片段。"""
        if start_line < 1 or end_line < start_line:
            raise ValueError("Invalid line range")

        file_path = _safe_resolve(config.workspace_root, relative_path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")

        lines = file_path.read_text(encoding="utf-8").splitlines()
        selection = lines[start_line - 1:end_line]
        return "\n".join(selection)

    @tool(approval_mode="never_require")
    def write_file(relative_path: str, content: str, append: bool = False) -> str:
        """写入工作区内文本文件（支持追加）。"""
        file_path = _safe_resolve(config.workspace_root, relative_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with file_path.open(mode=mode, encoding="utf-8") as file:
            file.write(content)

        return f"Wrote {len(content)} chars to {relative_path}"

    @tool(approval_mode="never_require")
    def run_command(command: str, timeout_seconds: int | None = None) -> str:
        """在工作区内执行白名单命令（如 python/pytest/pip）。"""
        tokens = command.strip().split()
        if not tokens:
            raise ValueError("Empty command")

        cmd_name = _normalize_command_name(tokens[0])
        if cmd_name not in config.allowed_commands:
            allowed = ", ".join(sorted(config.allowed_commands))
            raise ValueError(f"Command not allowed: {cmd_name}. Allowed: {allowed}")

        timeout = timeout_seconds or config.command_timeout_seconds
        result = subprocess.run(
            tokens,
            cwd=config.workspace_root,
            text=True,
            capture_output=True,
            shell=False,
            timeout=timeout,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output_parts = [
            f"ExitCode: {result.returncode}",
            f"Stdout:\n{stdout}" if stdout else "Stdout:\n",
            f"Stderr:\n{stderr}" if stderr else "Stderr:\n",
        ]
        return "\n\n".join(output_parts)

    return [read_file, write_file, run_command]
