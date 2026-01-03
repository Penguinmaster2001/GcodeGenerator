#! /bin/python


import json
import re
import sys
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import numpy as np

import svg_to_path
from gcode_types import GcodePoint

mplstyle.use(["dark_background", "ggplot", "fast"])

settings: dict[str, float] = {
    "bed_width": 200.0,
    "bed_depth": 200.0,
    "flow_rate": 0.55,
    "first_layer_height": 0.15,
    "layer_height": 0.1,
    "extruder_temp": 210,
    "bed_temp": 80,
    "retraction_distance": 0.1,
}
with open("settings.json", "r") as f:
    settings = json.load(f)["settings"]


# def display(points):
#     x_pts = []
#     y_pts = []
#     z_pts = []
#     for x, y, z in [(p.x, p.y, height_at_layer(p.layer)) for p in points]:
#         x_pts.append(x)
#         y_pts.append(y)
#         z_pts.append(z)


#     display_xyz(x_pts, y_pts, z_pts)
def display(points):
    xs_e, ys_e, zs_e = [], [], []
    xs_t, ys_t, zs_t = [], [], []
    for p in points:
        x, y, z = p.x, p.y, height_at_layer(p.layer)
        if p.extrude:
            xs_e.append(x)
            ys_e.append(y)
            zs_e.append(z)
        else:
            xs_t.append(x)
            ys_t.append(y)
            zs_t.append(z)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    ax.plot(xs_e, ys_e, zs_e, color="blue")
    ax.plot(xs_t, ys_t, zs_t, color="red", alpha=0.4)
    ax.set_box_aspect([1, 1, 0.4])  # x:y:z ratio
    
    ax.set_aspect("equal")
    plt.show()


def display_xyz(x, y, z):
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # ax.scatter(x, y, z)
    # ax.plot_surface(x, y, z)
    ax.plot(x, y, z)
    # ax.plot3D(x, y, z)

    ax.set_aspect("equal")
    plt.show()


def curve() -> list[GcodePoint]:
    def r1(theta, height):
        return 1.5 + (1.2 * np.cos(3.0 * theta))

    def r2(theta, height):
        return (
            (2.0 + (1.1 * (np.sin(3.0 * theta + 0.1 * height) ** 3.0))) ** 2.0
        ) / 5.0

    def r3(theta, height):
        return 2.0 * (1.0 + (((2.0 * height / 20.0) - 1.0) * np.cos(theta)))

    return polar(200, 200, 8.0, 200, 200, r3)


def polar(
    steps: int, layers: int, scale: float, width: float, depth: float, radius_func
) -> list[GcodePoint]:
    theta = np.linspace(0, 2 * np.pi, steps)

    points: list[GcodePoint] = []

    print(f"Height: {layers * settings['layer_height']}")

    for layer, height in enumerate(
        np.linspace(
            settings["first_layer_height"],
            settings["first_layer_height"] + (layers * settings["layer_height"]),
            layers,
            endpoint=False,
        )
    ):
        for x, y in zip(
            (scale * radius_func(theta, height) * np.cos(theta)) + (0.5 * width),
            (scale * radius_func(theta, height) * np.sin(theta)) + (0.5 * depth),
        ):
            points.append(GcodePoint(x, y, layer, True))

    return points  # np.array(x), np.array(y), np.array(z)


pattern = re.compile(
    r"^(?:G0|G1)\s*"
    r"(?P<x>X(-?\d+(?:\.\d+)?)\s*)?"
    r"(?P<y>Y(-?\d+(?:\.\d+)?)\s*)?"
    r"(?P<z>Z(-?\d+(?:\.\d+)?)\s*)?"
    r"(?P<e>E(-?\d+(?:\.\d+)?)\s*)?"
    r"$"
)


def match_xyz(line: str):
    m = pattern.fullmatch(line.strip())
    if m is None:
        return None  # no match

    def extract(key):
        val = m.group(key)  # e.g. "X12.34" or None
        if val is None:
            return None
        # remove the leading letter and convert to float if possible
        num = val[1:]
        if num == "":
            return None
        try:
            return float(num)
        except ValueError:
            return None

    return [extract("x"), extract("y"), extract("z"), extract("e")]


def display_gcode(gcode_file):
    x = [0.0]
    y = [0.0]
    z = [0.0]

    ave_ratio = 0.0
    num_ratio = 0

    with open(gcode_file) as f:
        for line in f.readlines():
            m = match_xyz(line)
            if m is not None:
                val = m[0]
                if val is None:
                    val = x[-1]
                x.append(val)

                val = m[1]
                if val is None:
                    val = y[-1]
                y.append(val)

                val = m[2]
                if val is None:
                    val = z[-1]
                z.append(val)

                val = m[3]
                if val is not None and val > 0.0:
                    dx = x[-1] - x[-2]
                    dy = y[-1] - y[-2]

                    length = np.sqrt((dx * dx) + (dy * dy))
                    if length > 0.001:
                        ave_ratio += val / length
                        num_ratio += 1

    print(len(x))
    if num_ratio > 0:
        print(ave_ratio / num_ratio)

    display_xyz(x, y, z)


def display_curve():
    display(curve())


def height_at_layer(layer: int):
    return settings["first_layer_height"] + (layer * settings["layer_height"])


def generate_curve(output_file):
    generate_gcode(output_file, curve())


def generate_svg(svg_file, output_file):
    generate_gcode(
        output_file, svg_to_path.generate_path_from_svg(svg_file, 500, 50, settings)
    )


def generate_gcode(output_file: str, points: list[GcodePoint]):
    text = ""
    with open("Fragments/starter.gcode", "r") as f:
        text += f.read()
    text += "\n\n\n;START\n"

    lx: float = points[0].x
    ly: float = points[0].y
    lz: float = height_at_layer(0)
    for cx, cy, cz, extrude in [
        (p.x, p.y, height_at_layer(p.layer), p.extrude) for p in points
    ]:
        if cx < 0.0:
            cx = 0
        elif cx > settings["bed_width"]:
            cx = 200.0

        if cy < 0.0:
            cy = 0
        elif cy > settings["bed_depth"]:
            cy = 200.0

        if cz < 0.0:
            cz = 0
        elif cz > 200.0:
            cz = 200.0

        extrusion: float = 0.0
        vals = []
        if not np.isclose(cx, lx, atol=0.001):
            vals.append(f"X{cx:.3f}")
            extrusion += (cx - lx) ** 2.0

        if not np.isclose(cy, ly, atol=0.001):
            vals.append(f"Y{cy:.3f}")
            extrusion += (cy - ly) ** 2.0

        if not np.isclose(cz, lz, atol=0.001):
            vals.append(f"Z{cz:.3f}")
            extrude = False

        extrusion = settings["flow_rate"] * np.sqrt(extrusion)
        # If no extrusion, ignore
        if not np.isclose(extrusion, 0.0, atol=0.001):
            # Retract
            if not extrude:
                # extrusion = -settings["retraction_distance"]
                extrusion = 0.0

            vals.append(f"E{extrusion:.3f}")

            text += f"G1 {' '.join(vals)}\n"

            lx = cx
            ly = cy
            lz = cz

    with open("Fragments/finisher.gcode", "r") as f:
        text += "\n;END\n\n\n"
        text += f.read()

    with open(output_file, "w") as f:
        f.write(text)


def display_svg(svg_file):
    display(svg_to_path.generate_path_from_svg(svg_file, 500, 50, settings))


commands: dict[str, tuple[Any, list[str]]] = {
    "disp-gcode": (display_gcode, ["gcode file"]),
    "disp-curve": (display_curve, []),
    "gen-curve": (generate_curve, ["output file"]),
    "disp-svg": (display_svg, ["svg file"]),
    "gen-svg": (generate_svg, ["svg file", "output file"]),
}


def format_command(command_name: str, command: tuple[Any, list[str]]):
    return f"{command_name} {' '.join([f'<{arg}>' for arg in command[1]])}"


if len(sys.argv) <= 1:
    print(f"Usage:\n\t{sys.argv[0]} <command> [args]")
    exit(1)

command_name = sys.argv[1].strip().lstrip("-").lower()
if command_name == "h" or command_name == "help":
    for command in commands:
        print(format_command(command, commands[command]))
    exit(0)


command = commands.get(command_name)
if command is None:
    print(f'Command unknown "{command_name}."\nUse "help" for list of commands.')
    exit(2)

if len(sys.argv) <= len(command[1]) + 1:
    print(f"Usage:\n\t{sys.argv[0]} {format_command(command_name, command)}")
    exit(3)

args = {}
for i, arg in enumerate(command[1]):
    args[arg.replace(" ", "_")] = sys.argv[i + 2]

command[0](**args)
