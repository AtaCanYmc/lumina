import os
import time

import click
import cv2

from lumina import __version__, flat_lithophane, generate_spiral_betty_png

BANNER = """
  __                     _
 / /   __  ______ ___  (_)___  ____ _
/ /   / / / / __ `__ \\/ / __ \\/ __ `/
/ /___/ /_/ / / / / / / / / / / /_/ /
/_____/\\__,_/_/ /_/ /_/_/_/ /_/\\__,_/
"""


def format_bytes(size_bytes: int) -> str:
    """Formats bytes into human readable binary units."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def format_duration(seconds: float) -> str:
    """Formats seconds into readable string."""
    if seconds < 1.0:
        return f"{seconds * 1000:.0f} ms"
    return f"{seconds:.2f} s"


def render_box(title: str, rows: list[tuple[str, str]]) -> str:
    """Renders a clean unicode terminal box with key-value pairs."""
    key_col_width = max(len(k) for k, _ in rows) + 1
    val_col_width = max(len(v) for _, v in rows)
    inner_width = max(key_col_width + val_col_width + 2, len(title) + 6, 48)

    top_title = f"─ {title} "
    top_border = f"┌{top_title}" + "─" * (inner_width - len(top_title)) + "┐"
    bottom_border = "└" + "─" * inner_width + "┘"

    lines = [click.style(top_border, fg="cyan")]
    for k, v in rows:
        k_str = f"{k}:"
        line_content = f" {k_str.ljust(key_col_width + 1)}{v}"
        pad = " " * (inner_width - len(line_content))
        lines.append(
            click.style("│", fg="cyan")
            + click.style(f" {k_str.ljust(key_col_width + 1)}", dim=True)
            + click.style(v, bold=True)
            + pad
            + click.style("│", fg="cyan")
        )
    lines.append(click.style(bottom_border, fg="cyan"))
    return "\n".join(lines)


def print_banner() -> None:
    """Prints Lumina brand ASCII header."""
    click.secho(BANNER, fg="cyan", bold=True)
    click.secho(
        f" Lithophane & Vector Art 3D Generator  •  v{__version__}\n",
        fg="bright_black",
    )


@click.group(invoke_without_command=True)
@click.version_option(__version__, "-v", "--version", prog_name="lumina")
@click.pass_context
def cli(ctx: click.Context):
    """Lumina: Lithophane & Spiral Betty 3D STL generator.

    Transform photographs into 3D-printable lithophane STLs and spiral vector art.
    """
    if ctx.invoked_subcommand is None:
        print_banner()
        click.echo(ctx.get_help())


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output STL file path. Defaults to input filename with .stl extension.",
)
@click.option("--width", "-w", default=100.0, help="Width of the lithophane in mm.")
@click.option("--height", "-h", default=150.0, help="Height of the lithophane in mm.")
@click.option(
    "--max-thick", default=3.0, help="Maximum thickness (for dark areas) in mm."
)
@click.option(
    "--min-thick", default=0.5, help="Minimum thickness (for light areas) in mm."
)
@click.option("--frame-thick", default=1.0, help="Thickness of the frame border in mm.")
@click.option(
    "--frame-height",
    default=2.0,
    help="Height of the frame border in mm (0 to auto-match max height).",
)
@click.option("--resolution", "-r", default=5, help="Resolution in pixels per mm.")
@click.option(
    "--shape",
    type=click.Choice(["rect", "circle", "heart"]),
    default="rect",
    help="Shape of the lithophane.",
)
@click.option(
    "--enhance/--no-enhance",
    default=False,
    help="Enhance image contrast before processing.",
)
@click.option(
    "--normalize/--no-normalize",
    default=False,
    help="Normalize image before processing.",
)
def flat(
    input_path: str,
    output: str | None,
    width: float,
    height: float,
    max_thick: float,
    min_thick: float,
    frame_thick: float,
    frame_height: float,
    resolution: int,
    shape: str,
    enhance: bool,
    normalize: bool,
):
    """Generates a flat lithophane STL from an image.

    INPUT_PATH: Path to the source image file.
    """
    start_time = time.perf_counter()
    click.secho(f"Processing {input_path}...", fg="cyan")

    try:
        click.secho(
            f"→ [1/3] Reading image and building mesh ({width:.1f} × {height:.1f} mm, {shape})...",
            dim=True,
        )
        mesh_obj = flat_lithophane(
            image_path=input_path,
            width_mm=width,
            height_mm=height,
            max_thickness=max_thick,
            min_thickness=min_thick,
            frame_thick_mm=frame_thick,
            frame_height_mm=frame_height,
            resolution=resolution,
            enhance=enhance,
            normalize=normalize,
            shape=shape,
        )

        click.secho("→ [2/3] Lithophane mesh computation complete.", dim=True)

        if output is None:
            base, _ = os.path.splitext(input_path)
            output = f"{base}.stl"

        output_dir = os.path.dirname(os.path.abspath(output))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        click.secho(f"→ [3/3] Saving STL to {output}...", dim=True)
        mesh_obj.save(output)

        elapsed = time.perf_counter() - start_time
        file_size = os.path.getsize(output) if os.path.exists(output) else 0
        triangle_count = len(mesh_obj.vectors)

        click.secho(f"\nSuccess! STL saved to: {output}", fg="green", bold=True)
        summary_rows = [
            ("Output File", os.path.abspath(output)),
            ("Dimensions", f"{width:.1f} × {height:.1f} mm"),
            ("Thickness", f"{min_thick:.2f} mm (min) .. {max_thick:.2f} mm (max)"),
            ("Frame", f"{frame_thick:.1f} mm width, {frame_height:.1f} mm height"),
            ("Shape", shape),
            ("Resolution", f"{resolution} px/mm"),
            ("Triangles", f"{triangle_count:,} facets"),
            ("File Size", format_bytes(file_size)),
            ("Time Elapsed", format_duration(elapsed)),
        ]
        click.echo(render_box("Lumina Lithophane Summary", summary_rows))

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output PNG file path.")
@click.option("--radius", "-r", default=100.0, help="Radius in mm.")
@click.option("--resolution", default=5, help="Resolution in pixels per mm.")
@click.option("--lines", default=30, help="Number of spiral lines.")
@click.option("--angle-step", default=0.05, help="Angle step for spiral.")
def spiral(
    input_path: str,
    output: str | None,
    radius: float,
    resolution: int,
    lines: int,
    angle_step: float,
):
    """Generates a spiral betty art image."""
    start_time = time.perf_counter()
    try:
        click.secho(f"Processing {input_path}...", fg="cyan")
        click.secho(
            f"→ [1/2] Computing spiral betty lines (radius={radius:.1f} mm, lines={lines})...",
            dim=True,
        )

        result = generate_spiral_betty_png(
            image_path=input_path,
            radius_mm=radius,
            resolution=resolution,
            lines=lines,
            angle_step=angle_step,
        )

        if output is None:
            base, _ = os.path.splitext(input_path)
            output = f"{base}_spiral.png"

        output_dir = os.path.dirname(os.path.abspath(output))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        click.secho(f"→ [2/2] Saving image to {output}...", dim=True)
        cv2.imwrite(output, result)

        elapsed = time.perf_counter() - start_time
        file_size = os.path.getsize(output) if os.path.exists(output) else 0
        h, w = result.shape[:2]

        click.secho(f"\nSuccess! Spiral art saved to: {output}", fg="green", bold=True)
        summary_rows = [
            ("Output File", os.path.abspath(output)),
            ("Image Size", f"{w} × {h} px"),
            ("Target Radius", f"{radius:.1f} mm"),
            ("Spiral Lines", str(lines)),
            ("Angle Step", f"{angle_step}"),
            ("Resolution", f"{resolution} px/mm"),
            ("File Size", format_bytes(file_size)),
            ("Time Elapsed", format_duration(elapsed)),
        ]
        click.echo(render_box("Lumina Spiral Summary", summary_rows))

    except Exception as e:
        raise click.ClickException(str(e)) from e


@cli.command("interactive", short_help="Interactive guided wizard for Lumina.")
@click.pass_context
def interactive(ctx: click.Context):
    """Guided step-by-step wizard for Lumina."""
    print_banner()
    click.secho("Interactive Wizard\n", fg="cyan", bold=True)
    click.echo("Select generation mode:")
    click.echo("  [1] Flat Lithophane  (3D printable STL mesh)")
    click.echo("  [2] Spiral Betty Art (2D continuous line spiral PNG)")
    mode = click.prompt("Mode", type=click.Choice(["1", "2"]), default="1")

    image_path = click.prompt(
        "Source image path",
        type=click.Path(exists=True, dir_okay=False, readable=True),
    )

    if mode == "1":
        click.secho("\n─── Lithophane Geometry ───", dim=True)
        width = click.prompt("Width (mm)", type=float, default=100.0)
        height = click.prompt("Height (mm)", type=float, default=150.0)
        shape = click.prompt(
            "Shape",
            type=click.Choice(["rect", "circle", "heart"]),
            default="rect",
        )
        resolution = click.prompt("Resolution (px/mm)", type=int, default=5)
        max_thick = click.prompt("Max thickness (mm)", type=float, default=3.0)
        min_thick = click.prompt("Min thickness (mm)", type=float, default=0.5)
        frame_thick = click.prompt(
            "Frame border thickness (mm)", type=float, default=1.0
        )
        frame_height = click.prompt("Frame border height (mm)", type=float, default=2.0)
        enhance = click.confirm("Enhance image contrast?", default=False)
        normalize = click.confirm("Normalize image?", default=False)

        base, _ = os.path.splitext(image_path)
        suggested_out = f"{base}.stl"
        output = click.prompt("Output STL path", default=suggested_out)

        click.echo("")
        if not click.confirm("Start generation with these settings?", default=True):
            click.secho("Cancelled.", fg="yellow")
            return

        ctx.invoke(
            flat,
            input_path=image_path,
            output=output,
            width=width,
            height=height,
            max_thick=max_thick,
            min_thick=min_thick,
            frame_thick=frame_thick,
            frame_height=frame_height,
            resolution=resolution,
            shape=shape,
            enhance=enhance,
            normalize=normalize,
        )
    else:
        click.secho("\n─── Spiral Art Settings ───", dim=True)
        radius = click.prompt("Radius (mm)", type=float, default=100.0)
        lines = click.prompt("Spiral lines count", type=int, default=30)
        resolution = click.prompt("Resolution (px/mm)", type=int, default=5)
        angle_step = click.prompt("Angle step", type=float, default=0.05)

        base, _ = os.path.splitext(image_path)
        suggested_out = f"{base}_spiral.png"
        output = click.prompt("Output PNG path", default=suggested_out)

        click.echo("")
        if not click.confirm("Start generation with these settings?", default=True):
            click.secho("Cancelled.", fg="yellow")
            return

        ctx.invoke(
            spiral,
            input_path=image_path,
            output=output,
            radius=radius,
            resolution=resolution,
            lines=lines,
            angle_step=angle_step,
        )


cli.add_command(interactive, name="wizard")


if __name__ == "__main__":
    cli()


def main():
    """Console script entry point expected by pyproject: lumina.cli:main

    Keeps backward compatibility with the current `cli()` function.
    """
    cli()
