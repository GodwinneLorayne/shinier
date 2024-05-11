from logging import getLogger
from pathlib import Path, PurePath
from typing import Annotated, Literal, Union
from venv import logger

from pydantic import BaseModel, Field

# graph.py
#
# This module defines a graph data structure for representing objects in the filesystem and in python.
# The graph is a directed graph, where each node has a value and a list of children.
# Since both the filesystem and python objects can form cycles, the graph must handle cycles.
# The graph will provide an iterator which will traverse the graph without following cycles.

logger = getLogger(__name__)

# ================================================================================
# Data Models
# ================================================================================


class DotPathModel(BaseModel):
    """A dot-separated path to a python object or for importing a python module Eg. 'package.module' or 'class.object'"""

    parts: Annotated[list[str], Field(description="The parts of the path")]


class BaseLocationModel(BaseModel):
    """A location in the filesystem or in python"""

    location_type: Annotated[
        str, Field(default="", description="The type of the location")
    ]


class FilesystemLocationModel(BaseLocationModel):
    """A location in the filesystem"""

    location_type: Annotated[
        Literal["filesystem"], Field(description="The type of the location")
    ] = "filesystem"
    file_path: Annotated[Path, Field(description="The path of the file or directory")]


class PythonModuleLocationModel(BaseLocationModel):
    """A location in a python module"""

    location_type: Annotated[
        Literal["python_module"], Field(description="The type of the location")
    ] = "python_module"
    file_path: Annotated[Path, Field(description="The path of the python module file")]
    import_root: Annotated[
        Path,
        Field(
            description="The path of the directory from which the module is imported"
        ),
    ]
    import_path: Annotated[
        DotPathModel, Field(description="The import path of the python module")
    ]


class PythonObjectLocationModel(BaseLocationModel):
    """A location in a python object"""

    location_type: Annotated[
        Literal["python_object"],
        Field(default="python_object", description="The type of the location"),
    ]
    file_path: Annotated[Path, Field(description="The path of the python module file")]
    import_root: Annotated[
        Path,
        Field(
            description="The path of the directory from which the module is imported"
        ),
    ]
    import_path: Annotated[
        DotPathModel, Field(description="The import path of the python module")
    ]
    ref_path: Annotated[
        DotPathModel, Field(description="The reference path of the python object")
    ]


LocationModel = Union[
    FilesystemLocationModel, PythonModuleLocationModel, PythonObjectLocationModel
]


class NameModel(BaseModel):
    """A name for a graph node"""

    short_name: Annotated[str, Field(description="The name of the object")]
    long_name: Annotated[
        str, Field(default="", description="The long name of the object")
    ]
    aliases: Annotated[
        list[str], Field(default_factory=list, description="The aliases of the object")
    ]


class BaseNodeModel(BaseModel):
    """A node in the graph"""

    node_type: Annotated[str, Field(description="The type of the node")] = ""
    location: LocationModel
    name: NameModel


class FilesystemNodeModel(BaseNodeModel):
    """A node in the graph representing a filesystem object"""

    node_type: Annotated[
        Literal["filesystem"], Field(description="The type of the node")
    ] = "filesystem"


class PythonModuleNodeModel(BaseNodeModel):
    """A node in the graph representing a python module"""

    node_type: Annotated[
        Literal["python_module"], Field(description="The type of the node")
    ] = "python_module"


class PythonObjectNodeModel(BaseNodeModel):
    """A node in the graph representing a python object"""

    node_type: Annotated[
        Literal["python_object"], Field(description="The type of the node")
    ] = "python_object"


NodeModel = Union[FilesystemNodeModel, PythonModuleNodeModel, PythonObjectNodeModel]


class GraphModel(BaseModel):
    """A graph data structure"""

    nodes: Annotated[
        list[NodeModel],
        Field(default_factory=list, description="The nodes in the graph"),
    ]
    edges: Annotated[
        dict[int, list[int]],
        Field(default_factory=dict, description="The edges in the graph"),
    ]


# ================================================================================
# Custom Exceptions
# ================================================================================


class PathDoesNotExistError(Exception):
    """Raised when a path does not exist"""

    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Path does not exist: {path}")


class PathIsNotFileOrDirectoryError(Exception):
    """Raised when a path is not a file or directory"""

    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Path is not a file or directory: {path}")


class PathIsNotPythonModuleError(Exception):
    """Raised when a path is not a python module"""

    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Path is not a python module: {path}")


# ================================================================================
# Runtime Classes
# ================================================================================


class Graph(GraphModel):
    """A graph data structure for representing objects in the filesystem and in python"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_node(self, node: NodeModel) -> bool:
        """Add a node to the graph"""
        if node not in self.nodes:
            self.nodes.append(node)
            return True

        return False

    def add_edge(self, parent_index: int, child_index: int):
        """Add an edge to the graph"""
        if parent_index not in self.edges:
            self.edges[parent_index] = []
        self.edges[parent_index].append(child_index)


# ================================================================================
# Free Functions
# ================================================================================


def is_path_python_module(path: PurePath) -> bool:
    """Check if a path is a python module"""

    return path.suffix == ".py"


def is_path_init_module(path: PurePath) -> bool:
    """Check if a path is an __init__.py module"""

    return path.name == "__init__.py"


def is_path_python_package(path: Path) -> bool:
    """Check if a path is a python package"""

    return path.is_dir() and (path / "__init__.py").exists()


def node_from_module_path(path: Path) -> PythonModuleNodeModel:
    """Split a path into the import root and import path"""

    if not is_path_python_module(path):
        raise PathIsNotPythonModuleError(path)

    import_root = path.parent
    if is_path_init_module(path):
        parts = []
        short_name = path.parent.name
        long_name = path.parent.name
    else:
        parts = [path.stem]
        short_name = path.stem
        long_name = path.name

    while is_path_python_package(import_root):
        parts.insert(0, import_root.name)
        import_root = import_root.parent

    return PythonModuleNodeModel(
        location=PythonModuleLocationModel(
            file_path=path,
            import_root=import_root,
            import_path=DotPathModel(parts=parts),
        ),
        name=NameModel(short_name=short_name, long_name=long_name, aliases=[]),
    )


def node_from_path(path: Path) -> NodeModel:
    """Create a node from a path"""

    if not path.exists():
        raise PathDoesNotExistError(path)

    while path.is_symlink():
        logger.debug(f"Resolving symlink: {path}")
        path = path.resolve()

    if not path.is_file() and not path.is_dir():
        raise PathIsNotFileOrDirectoryError(path)

    if path.is_dir():
        if is_path_python_package(path):
            return node_from_module_path(path / "__init__.py")

        return FilesystemNodeModel(
            location=FilesystemLocationModel(file_path=path),
            name=NameModel(short_name=path.name, long_name=path.name, aliases=[]),
        )

    if is_path_python_module(path):
        return node_from_module_path(path)

    return FilesystemNodeModel(
        location=FilesystemLocationModel(file_path=path),
        name=NameModel(short_name=path.stem, long_name=path.name, aliases=[]),
    )


def child_nodes_from_node(node: NodeModel) -> list[NodeModel]:
    """Get the child nodes of a node"""

    if isinstance(node, FilesystemNodeModel):
        path = node.location.file_path
        if path.is_dir():
            return [node_from_path(child) for child in path.iterdir()]
        return []

    if isinstance(node, PythonModuleNodeModel):
        path = node.location.file_path
        if is_path_init_module(path):
            return [
                node_from_path(child)
                for child in path.parent.iterdir()
                if child != path
            ]
        return []

    return []


def graph_from_path(path: Path) -> Graph:
    """Resolve the graph by following symlinks and imports"""

    node = node_from_path(path)

    graph = Graph(nodes=[node], edges={})

    # Breadth-first traversal
    index = 0
    while index < len(graph.nodes):
        node = graph.nodes[index]
        children = child_nodes_from_node(node)
        for child in children:
            if graph.add_node(child):
                child_index = len(graph.nodes) - 1
                graph.add_edge(index, child_index)

        index += 1

    return graph
