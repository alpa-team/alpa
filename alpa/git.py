"""
Wrapper around git cmd using subprocess
"""
import asyncio
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitCmdResult:
    stdout: str
    stderr: str
    retval: int


class GitCMD:
    def __init__(self, cwd: str) -> None:
        self.git_root = cwd
        output = self.git_cmd(["rev-parse", "--show-toplevel"])
        if "not a git repository" in output.stderr:
            raise FileNotFoundError(output.stderr)

        self.git_root = output.stdout.strip()

    def git_cmd(
        self, arguments: list[str], cwd: Optional[str] = None
    ) -> "GitCmdResult":
        if cwd is None:
            context = self.git_root
        else:
            context = cwd

        process = subprocess.run(
            ["git"] + arguments,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=context,
        )
        return GitCmdResult(
            stdout=process.stdout.decode().strip(),
            stderr=process.stderr.decode().strip(),
            retval=process.returncode,
        )

    async def async_git_cmd(
        self, arguments: list[str], cwd: Optional[str] = None
    ) -> "GitCmdResult":
        if cwd is None:
            context = self.git_root
        else:
            context = cwd

        async_subprocess = await asyncio.create_subprocess_exec(
            "git",
            *arguments,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=context,
        )
        stdout, stderr = await async_subprocess.communicate()
        return GitCmdResult(
            stdout=stdout.decode().strip(),
            stderr=stderr.decode().strip(),
            retval=async_subprocess.returncode,  # type: ignore
        )
