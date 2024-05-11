from pathlib import Path

from shinier.graph import (
    DotPathModel,
    FilesystemLocationModel,
    FilesystemNodeModel,
    Graph,
    NameModel,
    PythonModuleLocationModel,
    PythonModuleNodeModel,
    child_nodes_from_node,
    graph_from_path,
    is_path_python_package,
    node_from_path,
)


def test_node_from_path_dir(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    expected_node = FilesystemNodeModel(
        location=FilesystemLocationModel(file_path=dir_0),
        name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
    )

    node = node_from_path(dir_0)

    assert node == expected_node


def test_node_from_path_file(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_node = FilesystemNodeModel(
        location=FilesystemLocationModel(file_path=file_0),
        name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
    )

    node = node_from_path(file_0)

    assert node == expected_node


def test_node_from_path_file_with_extension(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0.txt"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_node = FilesystemNodeModel(
        location=FilesystemLocationModel(file_path=file_0),
        name=NameModel(
            short_name=file_0.stem,
            long_name=file_0.name,
        ),
    )

    node = node_from_path(file_0)

    assert node == expected_node


def test_node_from_path_python_module(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0.py"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_node = PythonModuleNodeModel(
        location=PythonModuleLocationModel(
            file_path=file_0,
            import_root=tmp_path,
            import_path=DotPathModel(parts=["file_0"]),
        ),
        name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
    )

    node = node_from_path(file_0)

    assert node == expected_node


def test_node_from_path_python_module_with_package(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    file_0 = dir_0 / "file_0.py"
    file_0.touch()

    expected_node = PythonModuleNodeModel(
        location=PythonModuleLocationModel(
            file_path=file_0,
            import_root=tmp_path,
            import_path=DotPathModel(parts=["dir_0", "file_0"]),
        ),
        name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
    )

    node = node_from_path(file_0)

    assert node == expected_node


def test_node_from_path_python_module_with_package_and_subpackage(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    dir_1 = dir_0 / "dir_1"
    dir_1.mkdir()

    assert not is_path_python_package(dir_1)

    init_1 = dir_1 / "__init__.py"
    init_1.touch()

    assert is_path_python_package(dir_1)

    file_0 = dir_1 / "file_0.py"
    file_0.touch()

    expected_node = PythonModuleNodeModel(
        location=PythonModuleLocationModel(
            file_path=file_0,
            import_root=tmp_path,
            import_path=DotPathModel(parts=["dir_0", "dir_1", "file_0"]),
        ),
        name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
    )

    node = node_from_path(file_0)

    assert node == expected_node


def test_node_from_path_python_init_module(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    expected_node = PythonModuleNodeModel(
        location=PythonModuleLocationModel(
            file_path=init_0,
            import_root=tmp_path,
            import_path=DotPathModel(parts=["dir_0"]),
        ),
        name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
    )

    node = node_from_path(init_0)

    assert node == expected_node


def test_node_from_path_symlink_not_cycle(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not dir_0.is_symlink()
    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    dir_1 = tmp_path / "dir_1"
    dir_1.symlink_to(dir_0)

    assert dir_1.is_symlink()
    assert not is_path_python_package(dir_1)

    assert dir_1.resolve() == dir_0

    expected_node = FilesystemNodeModel(
        location=FilesystemLocationModel(file_path=dir_0),
        name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
    )

    node = node_from_path(dir_1)

    assert node == expected_node


def test_node_from_path_symlink_cycle(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not dir_0.is_symlink()
    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    dir_1 = tmp_path / "dir_1"
    dir_1.symlink_to(dir_0)

    assert dir_1.is_symlink()
    assert not is_path_python_package(dir_1)

    dir_0_symlink = dir_0 / "dir_0_symlink"
    dir_0_symlink.symlink_to(dir_1)

    assert dir_0_symlink.is_symlink()
    assert not is_path_python_package(dir_0_symlink)

    assert dir_0_symlink.resolve() == dir_0

    expected_node = FilesystemNodeModel(
        location=FilesystemLocationModel(file_path=dir_0),
        name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
    )

    node = node_from_path(dir_0_symlink)

    assert node == expected_node


def test_graph_from_path_dir(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    expected_graph = Graph()

    expected_graph.nodes = [
        FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=dir_0),
            name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(dir_0)

    assert graph == expected_graph


def test_graph_from_path_file(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_graph = Graph()

    expected_graph.nodes = [
        FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=file_0),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(file_0)

    assert graph == expected_graph


def test_graph_from_path_python_module(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0.py"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_graph = Graph()

    expected_graph.nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=file_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["file_0"]),
            ),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(file_0)

    assert graph == expected_graph


def test_graph_from_path_python_module_with_package(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    file_0 = dir_0 / "file_0.py"
    file_0.touch()

    expected_graph = Graph()

    expected_graph.nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=file_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0", "file_0"]),
            ),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(file_0)

    assert graph == expected_graph


def test_graph_from_path_python_module_with_package_and_subpackage(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    dir_1 = dir_0 / "dir_1"
    dir_1.mkdir()

    assert not is_path_python_package(dir_1)

    init_1 = dir_1 / "__init__.py"
    init_1.touch()

    assert is_path_python_package(dir_1)

    file_0 = dir_1 / "file_0.py"
    file_0.touch()

    expected_graph = Graph()

    expected_graph.nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=file_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0", "dir_1", "file_0"]),
            ),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(file_0)

    assert graph == expected_graph


def test_graph_from_path_python_init_module(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    expected_graph = Graph()

    expected_graph.nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=init_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0"]),
            ),
            name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(init_0)

    assert graph == expected_graph


def test_graph_from_path_symlink_not_cycle(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not dir_0.is_symlink()
    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    dir_1 = tmp_path / "dir_1"
    dir_1.symlink_to(dir_0)

    assert dir_1.is_symlink()
    assert not is_path_python_package(dir_1)

    assert dir_1.resolve() == dir_0

    expected_graph = Graph()

    expected_graph.nodes = [
        FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=dir_0),
            name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(dir_1)

    assert graph == expected_graph


def test_graph_from_path_symlink_cycle(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not dir_0.is_symlink()
    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    dir_1 = tmp_path / "dir_1"
    dir_1.symlink_to(dir_0)

    assert dir_1.is_symlink()
    assert not is_path_python_package(dir_1)

    dir_0_symlink = dir_0 / "dir_0_symlink"
    dir_0_symlink.symlink_to(dir_1)

    assert dir_0_symlink.is_symlink()
    assert not is_path_python_package(dir_0_symlink)

    assert dir_0_symlink.resolve() == dir_0

    expected_graph = Graph()

    expected_graph.nodes = [
        FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=dir_0),
            name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
        )
    ]

    expected_graph.edges = {}

    graph = graph_from_path(dir_0_symlink)

    assert graph == expected_graph


def test_child_nodes_from_node_dir(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    expected_child_nodes = [
        FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=dir_0),
            name=NameModel(short_name=dir_0.name, long_name=dir_0.name, aliases=[]),
        )
    ]

    node = node_from_path(tmp_path)

    child_nodes = child_nodes_from_node(node)

    assert child_nodes == expected_child_nodes


def test_child_nodes_from_node_file(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_child_nodes = [
        FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=file_0),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    node = node_from_path(tmp_path)

    child_nodes = child_nodes_from_node(node)

    assert child_nodes == expected_child_nodes


def test_child_nodes_from_node_python_module(tmp_path: Path):
    tmp_path.exists()
    file_0 = tmp_path / "file_0.py"
    file_0.touch()

    assert not is_path_python_package(tmp_path)

    expected_child_nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=file_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["file_0"]),
            ),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    node = node_from_path(tmp_path)

    child_nodes = child_nodes_from_node(node)

    assert child_nodes == expected_child_nodes


def test_child_nodes_from_node_python_module_with_package(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    file_0 = dir_0 / "file_0.py"
    file_0.touch()

    expected_child_nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=file_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0", "file_0"]),
            ),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        )
    ]

    node = node_from_path(dir_0)

    child_nodes = child_nodes_from_node(node)

    assert child_nodes == expected_child_nodes


def test_graph_from_path_python_module_with_package_and_subpackage_root(tmp_path: Path):
    tmp_path.exists()
    dir_0 = tmp_path / "dir_0"
    dir_0.mkdir()

    assert not is_path_python_package(tmp_path)
    assert not is_path_python_package(dir_0)

    init_0 = dir_0 / "__init__.py"
    init_0.touch()

    assert is_path_python_package(dir_0)

    dir_1 = dir_0 / "dir_1"
    dir_1.mkdir()

    assert not is_path_python_package(dir_1)

    init_1 = dir_1 / "__init__.py"
    init_1.touch()

    assert is_path_python_package(dir_1)

    file_0 = dir_1 / "file_0.py"
    file_0.touch()

    expected_graph = Graph()

    expected_graph.nodes = [
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=init_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0"]),
            ),
            name=NameModel(short_name=dir_0.stem, long_name=dir_0.name, aliases=[]),
        ),
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=init_1,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0", "dir_1"]),
            ),
            name=NameModel(short_name=dir_1.stem, long_name=dir_1.name, aliases=[]),
        ),
        PythonModuleNodeModel(
            location=PythonModuleLocationModel(
                file_path=file_0,
                import_root=tmp_path,
                import_path=DotPathModel(parts=["dir_0", "dir_1", "file_0"]),
            ),
            name=NameModel(short_name=file_0.stem, long_name=file_0.name, aliases=[]),
        ),
    ]

    expected_graph.edges = {0: [1], 1: [2]}

    graph = graph_from_path(dir_0)

    assert graph == expected_graph
