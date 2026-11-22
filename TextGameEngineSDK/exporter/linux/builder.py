
import shutil
import stat
import subprocess
from pathlib import Path
import os


class Builder:
    def __init__(self, source, runtime, output, entry="main.py"):
        self.source = Path(source).resolve()
        self.runtime = Path(runtime).resolve()
        self.output = Path(output).resolve()
        self.entry = Path(entry)

    

    def validate(self):
        if not self.source.is_dir():
            raise NotADirectoryError(
                f"Project directory not found: {self.source}"
            )

        if not self.runtime.is_dir():
            raise FileNotFoundError(
                f"Runtime directory not found: {self.runtime}"
            )

        if not (self.runtime / "lib").is_dir():
            raise RuntimeError("Invalid CPython runtime: missing lib/")

        if self.entry.is_absolute() or ".." in self.entry.parts:
            raise ValueError("Entry point must be inside the project")

        entry_file = self.source / self.entry

        if not entry_file.is_file() or entry_file.suffix != ".py":
            raise FileNotFoundError(
                f"Python entry point not found: {entry_file}"
            )

        candidates = [
            self.runtime / "bin" / "python3",
            self.runtime / "bin" / "python",
        ]

        candidates += sorted(
            (self.runtime / "bin").glob("python3.*")
        )

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        raise RuntimeError("Could not find CPython executable")

    def build(self):
        python = self.validate()

        if self.output.exists():
            shutil.rmtree(self.output)

        self.output.mkdir(parents=True)

        app_dir = self.output / "app"
        runtime_dir = self.output / "runtime"

        print("[SourcePack] Copying project...")


        print("[SourcePack] Copying project...")

        shutil.copytree(
            self.source,
            app_dir,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.pyc",
                ".git",
                ".venv",
                "venv",
                "dist",
                "build",
                "*.py",
                "*.cpp",
                "*.sh",
                ".gitignore",
                "replay_frames",
                "build",
                "buildHatred",
                ".vscode",
                "*.inventory",
                "run"
            )
        )


        import py_compile

        for root, dirs, files in os.walk(self.source):
            dirs[:] = [
                d for d in dirs
                if d not in {"__pycache__", ".git", ".venv", "venv"}
            ]

            for filename in files:
                if not filename.endswith(".py"):
                    continue

                source_file = Path(root) / filename
                relative = source_file.relative_to(self.source)

                output_file = app_dir / relative.with_suffix(".pyc")
                output_file.parent.mkdir(parents=True, exist_ok=True)

                py_compile.compile(
                    str(source_file),
                    cfile=str(output_file),
                    dfile=str(relative),
                    doraise=True
                )


        print("[SourcePack] Copying CPython...")

        shutil.copytree(
            self.runtime,
            runtime_dir,
            symlinks=True
        )

        print("[SourcePack] Creating launcher...")

        relative_python = python.relative_to(self.runtime)


        entry_pyc = self.entry.with_suffix(".pyc")

        launcher = self.output / "run"

        launcher.write_text(
            "#!/bin/sh\n"
            'HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"\n'
            'cd "$HERE/app" || exit 1\n'
            f'exec "$HERE/runtime/{relative_python}" '
            f'"$HERE/app/{entry_pyc.as_posix()}" "$@"\n'
        )


        launcher.chmod(
            launcher.stat().st_mode |
            stat.S_IXUSR |
            stat.S_IXGRP |
            stat.S_IXOTH
        )

        print("[SourcePack] Testing bundled Python...")

        subprocess.run(
            [str(runtime_dir / relative_python), "--version"],
            check=True
        )

        print("[SourcePack] Build complete!")
        print(f"[SourcePack] Output: {self.output}")
