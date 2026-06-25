from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    ".cache",
    "cache",
    "data",
    "outputs",
    "logs",
    "build",
    "dist",
    "models",
    "checkpoints",
    "weights",
}


def find_project_root(start_path: Path) -> Path:
    """
    Walk upward until a project marker is found.
    """

    current = start_path.resolve()

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current

        if (current / ".git").exists():
            return current

        current = current.parent

    raise FileNotFoundError(
        "Could not locate project root. " "Expected 'pyproject.toml' or '.git'."
    )


def write_tree(file, directory: Path, prefix: str = ""):
    """
    Recursively write folder tree.
    """

    entries = sorted(
        [item for item in directory.iterdir() if item.name not in IGNORE_DIRS],
        key=lambda x: (not x.is_dir(), x.name.lower()),
    )

    for index, entry in enumerate(entries):
        is_last = index == len(entries) - 1

        connector = "└── " if is_last else "├── "

        file.write(f"{prefix}{connector}{entry.name}\n")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            write_tree(file, entry, prefix + extension)


def main():
    script_dir = Path(__file__).resolve().parent

    project_root = find_project_root(script_dir)

    output_file = project_root / "docs" / "project_structure.txt"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"{project_root.name}\n")
        write_tree(f, project_root)

    print(f"Tree generated successfully:")
    print(output_file)


if __name__ == "__main__":
    main()
