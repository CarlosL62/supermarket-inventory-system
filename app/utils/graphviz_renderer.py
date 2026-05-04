from graphviz import Digraph
from html import escape


def get_path_edges(path):
    edges = set()

    if path is None:
        return edges

    for index in range(len(path) - 1):
        edges.add((path[index], path[index + 1]))

    return edges


def safe_html(value):
    return escape(str(value), quote=True)


def format_tree_value(value, value_fields=None):
    if value is None:
        return ""

    if isinstance(value, (str, int, float)):
        return str(value)

    if hasattr(value, "__dict__"):
        attributes = vars(value)

        if value_fields is not None:
            for field in value_fields:
                if field in attributes and attributes[field] is not None:
                    return format_tree_value(attributes[field], value_fields)

        preferred_fields = (
            "key", "value", "data", "product", "item", "record",
            "barcode", "name", "product_name", "category",
            "expiration_date", "expiry_date", "expiration", "date"
        )

        for field in preferred_fields:
            if field in attributes and attributes[field] is not None:
                return format_tree_value(attributes[field], value_fields)

        for field, field_value in attributes.items():
            if field in ("left", "right", "height", "children", "parent"):
                continue
            if field_value is not None:
                return format_tree_value(field_value, value_fields)

    return str(value)


def build_branch_graph_svg(branches, connections, highlighted_time_path=None, highlighted_cost_path=None, current_branch_id=None):
    time_edges = get_path_edges(highlighted_time_path)
    cost_edges = get_path_edges(highlighted_cost_path)

    dot = Digraph("branch_graph", format="svg")
    dot.attr(
        rankdir="LR",
        bgcolor="#eef2f7",
        splines="spline",
        overlap="false",
        nodesep="0.45",
        ranksep="0.65",
        ratio="compress",
        margin="0",
        pad="0.1",
        fontname="Arial"
    )

    dot.attr(label="Rojo: menor tiempo | Verde: menor costo | Morado: ambas rutas", labelloc="t", fontsize="12", fontcolor="#111827")

    dot.attr(
        "node",
        shape="ellipse",
        style="filled",
        fillcolor="#dbeafe",
        color="#0f172a",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="10",
        margin="0.14,0.08",
        fixedsize="false"
    )

    dot.attr(
        "edge",
        color="#1f2937",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="10",
        penwidth="2"
    )

    for branch in branches:
        label = f"{branch.id}\n{branch.name}"

        if current_branch_id is not None and branch.id == current_branch_id:
            dot.node(
                str(branch.id),
                label,
                fillcolor="#fde68a",
                color="#d97706",
                penwidth="4"
            )
        else:
            dot.node(str(branch.id), label)

    for source_id, destination_id, time_weight, cost_weight, is_bidirectional in connections:
        label = f"T:{time_weight} | C:{cost_weight}"

        is_time_edge = (source_id, destination_id) in time_edges
        is_cost_edge = (source_id, destination_id) in cost_edges
        is_reverse_time_edge = is_bidirectional and (destination_id, source_id) in time_edges
        is_reverse_cost_edge = is_bidirectional and (destination_id, source_id) in cost_edges

        belongs_to_time_path = is_time_edge or is_reverse_time_edge
        belongs_to_cost_path = is_cost_edge or is_reverse_cost_edge

        if belongs_to_time_path and belongs_to_cost_path:
            edge_color = "#7c3aed"
            pen_width = "5"
            label = f"Ambas rutas | {label}"
        elif belongs_to_time_path:
            edge_color = "#dc2626"
            pen_width = "4"
            label = f"Menor tiempo | {label}"
        elif belongs_to_cost_path:
            edge_color = "#16a34a"
            pen_width = "4"
            label = f"Menor costo | {label}"
        else:
            edge_color = "#2563eb" if is_bidirectional else "#1f2937"
            pen_width = "2"

        if is_bidirectional:
            dot.edge(
                str(source_id),
                str(destination_id),
                label=label,
                dir="both",
                color=edge_color,
                fontcolor="#111827",
                fontname="Arial",
                penwidth=pen_width
            )
        else:
            dot.edge(
                str(source_id),
                str(destination_id),
                label=label,
                dir="forward",
                color=edge_color,
                fontcolor="#111827",
                fontname="Arial",
                penwidth=pen_width
            )

    return dot.pipe(format="svg")


def build_binary_tree_svg(root, title="Árbol binario", value_fields=None):
    dot = Digraph("binary_tree", format="svg")
    dot.attr(
        rankdir="TB",
        bgcolor="#eef2f7",
        splines="line",
        nodesep="0.45",
        ranksep="0.7",
        margin="0",
        pad="0.1",
        fontname="Arial",
        label=title,
        labelloc="t",
        fontsize="12",
        fontcolor="#111827"
    )

    dot.attr(
        "node",
        shape="ellipse",
        style="filled",
        fillcolor="#dbeafe",
        color="#0f172a",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="10",
        margin="0.12,0.08"
    )

    dot.attr(
        "edge",
        color="#1f2937",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="10",
        penwidth="2"
    )

    if root is None:
        dot.node("empty", "Vacío", shape="box")
        return dot.pipe(format="svg")

    def get_node_value(node):
        for attr in ("key", "value", "data", "product", "item", "record", "barcode", "name", "product_name"):
            if hasattr(node, attr):
                return format_tree_value(getattr(node, attr), value_fields)

        return format_tree_value(node, value_fields)

    def add_node(node):
        node_id = str(id(node))
        dot.node(node_id, get_node_value(node))

        left = getattr(node, "left", None)
        right = getattr(node, "right", None)

        if left is not None:
            left_id = add_node(left)
            dot.edge(node_id, left_id)

        if right is not None:
            right_id = add_node(right)
            dot.edge(node_id, right_id)

        return node_id

    add_node(root)
    return dot.pipe(format="svg")


def build_multiway_tree_svg(root, title="Árbol", value_fields=None, show_leaf_links=False):
    dot = Digraph("multiway_tree", format="svg")
    dot.attr(
        rankdir="TB",
        bgcolor="#eef2f7",
        splines="line",
        nodesep="0.5",
        ranksep="0.75",
        margin="0",
        pad="0.1",
        fontname="Arial",
        label=title,
        labelloc="t",
        fontsize="12",
        fontcolor="#111827"
    )

    dot.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fillcolor="#dcfce7",
        color="#14532d",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="11",
        margin="0.12,0.08"
    )

    dot.attr(
        "edge",
        color="#1f2937",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="10",
        penwidth="2"
    )

    if root is None:
        dot.node("empty", "Vacío", shape="box")
        return dot.pipe(format="svg")

    leaf_nodes = []

    def get_node_keys(node):
        for attr in ("keys", "values", "data"):
            if hasattr(node, attr):
                keys = getattr(node, attr)

                if isinstance(keys, list):
                    return [format_tree_value(key, value_fields) for key in keys]

                return [format_tree_value(keys, value_fields)]

        return [format_tree_value(node, value_fields)]

    def get_node_children(node):
        for attr in ("children", "child", "sons"):
            if hasattr(node, attr):
                return getattr(node, attr)
        return []

    def is_leaf_node(node):
        for attr in ("is_leaf", "leaf"):
            if hasattr(node, attr):
                return bool(getattr(node, attr))

        return len(get_node_children(node)) == 0

    def add_node(node):
        node_id = str(id(node))
        keys = get_node_keys(node)
        label = "  |  ".join(keys)
        dot.node(node_id, label)

        if show_leaf_links and is_leaf_node(node):
            leaf_nodes.append(node)

        for child in get_node_children(node):
            if child is None:
                continue

            child_id = add_node(child)
            dot.edge(node_id, child_id)

        return node_id

    add_node(root)

    if show_leaf_links and len(leaf_nodes) > 1:
        for index in range(len(leaf_nodes) - 1):
            current_leaf_id = str(id(leaf_nodes[index]))
            next_leaf_id = str(id(leaf_nodes[index + 1]))
            dot.edge(
                current_leaf_id,
                next_leaf_id,
                color="#2563eb",
                style="dashed",
                penwidth="2",
                constraint="false",
            )

    return dot.pipe(format="svg")


def build_hash_table_svg(hash_table, title="Hash Table"):
    dot = Digraph("hash_table", format="svg")
    dot.attr(
        rankdir="TB",
        bgcolor="#eef2f7",
        splines="line",
        nodesep="0.45",
        ranksep="0.75",
        margin="0",
        pad="0.1",
        fontname="Arial",
        label=title,
        labelloc="t",
        fontsize="12",
        fontcolor="#111827"
    )
    dot.attr("node", shape="plaintext", fontname="Arial")
    dot.attr("edge", color="#64748b", arrowsize="0.7")

    if hash_table is None:
        dot.node(
            "empty",
            label="<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0' CELLPADDING='8'>"
                  "<TR><TD BGCOLOR='#fee2e2'><B>Hash Table not found</B></TD></TR>"
                  "</TABLE>>"
        )
        return dot.pipe(format="svg")

    table = getattr(hash_table, "table", [])
    capacity = getattr(hash_table, "capacity", len(table))
    used_buckets = sum(1 for bucket in table if bucket)
    total_products = sum(len(bucket) for bucket in table)
    collisions = sum(max(0, len(bucket) - 1) for bucket in table)
    load_factor = total_products / capacity if capacity else 0

    summary_label = (
        f"<<TABLE BORDER='2' CELLBORDER='1' CELLSPACING='0' CELLPADDING='7'>"
        f"<TR><TD COLSPAN='2' BGCOLOR='#c7d2fe'><B>Resumen de Hash Table</B></TD></TR>"
        f"<TR><TD><B>Capacidad</B></TD><TD>{capacity}</TD></TR>"
        f"<TR><TD><B>Buckets usados</B></TD><TD>{used_buckets}</TD></TR>"
        f"<TR><TD><B>Total productos</B></TD><TD>{total_products}</TD></TR>"
        f"<TR><TD><B>Colisiones</B></TD><TD>{collisions}</TD></TR>"
        f"<TR><TD><B>Factor de carga</B></TD><TD>{load_factor:.4f}</TD></TR>"
        f"</TABLE>>"
    )
    dot.node("summary", label=summary_label)
    dot.node(
        "bucket_section",
        label="<<TABLE BORDER='0' CELLBORDER='0' CELLSPACING='0' CELLPADDING='4'>"
              "<TR><TD><B>Buckets ocupados</B></TD></TR>"
              "</TABLE>>"
    )
    dot.edge("summary", "bucket_section", style="invis")

    bucket_nodes = []

    for index, bucket in enumerate(table):
        if not bucket:
            continue

        bucket_id = f"bucket_{index}"
        bucket_nodes.append(bucket_id)
        bucket_color = "#fecaca" if len(bucket) > 1 else "#dbeafe"
        bucket_label = (
            f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0' CELLPADDING='6'>"
            f"<TR><TD BGCOLOR='{bucket_color}'><B>Bucket {index}</B></TD></TR>"
            f"<TR><TD>Items: {len(bucket)}</TD></TR>"
            f"</TABLE>>"
        )
        dot.node(bucket_id, label=bucket_label)

        dot.edge("bucket_section", bucket_id, style="invis", constraint="false")
        previous_id = bucket_id

        for product_index, product in enumerate(bucket):
            product_id = f"bucket_{index}_product_{product_index}"
            product_name = safe_html(getattr(product, "name", "Producto"))
            barcode = safe_html(getattr(product, "barcode", ""))
            product_label = (
                f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0' CELLPADDING='6'>"
                f"<TR><TD BGCOLOR='#dcfce7'><B>{product_name}</B></TD></TR>"
                f"<TR><TD>{barcode}</TD></TR>"
                f"</TABLE>>"
            )
            dot.node(product_id, label=product_label)
            dot.edge(previous_id, product_id)
            previous_id = product_id

    return dot.pipe(format="svg")