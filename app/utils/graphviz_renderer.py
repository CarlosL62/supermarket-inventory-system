from graphviz import Digraph


def get_path_edges(path):
    edges = set()

    if path is None:
        return edges

    for index in range(len(path) - 1):
        edges.add((path[index], path[index + 1]))

    return edges


def build_branch_graph_svg(branches, connections, highlighted_time_path=None, highlighted_cost_path=None):
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
        shape="circle",
        style="filled",
        fillcolor="#dbeafe",
        color="#0f172a",
        fontcolor="#111827",
        fontname="Arial",
        fontsize="11",
        width="1.0",
        fixedsize="true"
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