import nuke

def check_outside_nodes():
    read_types = ("Read", "ReadGeo", "ReadGeo2")
    script_base = "/".join(nuke.toNode("root").knob("name").value().split("/")[0:5])
    failed_nodes = []
    msg = u"\nThese nodes are outside of the script, please fix:\n"

    for node in nuke.allNodes():
        if node.Class() in read_types:
            if script_base != "/".join(node.knob("file").value().split("/")[0:5]):
                failed_nodes.append(node.name())

    if failed_nodes:
        for node in failed_nodes:
            msg += node + "\n"
        nuke.message(msg)
        raise BaseException