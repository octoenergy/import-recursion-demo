# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click~=8.1",
# ]
# ///
from textwrap import dedent
import click
from pathlib import Path

import shutil

PROJECT_ROOT = Path(__file__).parent

PACKAGE_NAME = "myproject"


@click.command()
@click.option("--project-name", default="demo")
@click.option("--chain-length", default=150)
@click.option("--recursion-limit", default=1000)
def generate(project_name: str, chain_length: int, recursion_limit: int) -> None:
    """
    Generate a Python project with an import chain of the supplied length.

    Args:
        project_name: The name of the project, created under src/{project_name}. If a project of that name
                      already exists, it will be overwritten.
        chain_length: The length of the import chain triggered by running main.py.
        recursion_limit: The Python recursion limit that will be set before triggering the import chain.

    For the project structure, see the repository README.
    """
    src_path = PROJECT_ROOT / "src"
    package_path = src_path / project_name

    # Create the src, if it doesn't exist.
    src_path.mkdir(exist_ok=True)
    # Remove the existing package, if it exists.
    shutil.rmtree(package_path, ignore_errors=True)

    _create_package_and_main(package_path, project_name, chain_length, recursion_limit)

    # Create modules for each link in import chain.
    for position in range(1, chain_length + 1):
        if (position - 1) % 10 == 0:
            print(f"Writing {position}/{chain_length}.")
        is_last_module = position == chain_length
        _create_module(package_path, position, is_last_module)

    print(f"Generated demo project at {package_path}.")
    print("You can now run the project like this:\n")
    print(f"    uv run src/{project_name}/main.py\n")


def _create_package_and_main(
    package_path: Path, project_name: str, chain_length: int, recursion_limit: int
) -> None:
    package_path.mkdir()
    (package_path / f"__init__.py").write_text("")
    (package_path / "main.py").write_text(
        dedent(f"""\
            from pathlib import Path
            import sys

            # Add the src directory to the Python path so we can import this package.
            PATH_TO_SRC = Path(__file__).parent.parent
            sys.path.append(str(PATH_TO_SRC))

            sys.setrecursionlimit({recursion_limit})
            
            print(f"Importing a chain of {chain_length} modules with a recursion limit of {recursion_limit}...")
            
            # Begin the chain of imports.
            from {project_name} import mod_001
            """)
    )


def _create_module(
    package_path: Path, position_in_chain: int, is_last_module: bool
) -> None:
    module_name = f"mod_{str(position_in_chain).zfill(3)}"
    if is_last_module:
        # The last module - print a message.
        module_contents = 'print("Got to the end of the import chain.")'
    else:
        # Module should import the next module.
        next_i = position_in_chain + 1
        next_module_name = f"mod_{str(next_i).zfill(3)}"
        module_contents = f"from . import {next_module_name}"

    (package_path / f"{module_name}.py").write_text(module_contents)


if __name__ == "__main__":
    generate()
    # generate(project_name="demo", chain_length=100, recursion_limit=100)
