import click
import os
import cv2
from lumina import flat_lithophane, generate_spiral_betty_png


@click.group()
def cli():
    """Lumina: generating lithophane STLs.
    
    A CLI tool for generating lithophane STLs from images.
    """
    pass


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None,
              help='Output STL file path. Defaults to input filename with .stl extension.')
@click.option('--width', '-w', default=100.0, help='Width of the lithophane in mm.')
@click.option('--height', '-h', default=150.0, help='Height of the lithophane in mm.')
@click.option('--max-thick', default=3.0, help='Maximum thickness (for dark areas) in mm.')
@click.option('--min-thick', default=0.5, help='Minimum thickness (for light areas) in mm.')
@click.option('--frame-thick', default=1.0, help='Thickness of the frame border in mm.')
@click.option('--frame-height', default=2.0, help='Height of the frame border in mm (0 to auto-match max height).')
@click.option('--resolution', '-r', default=5, help='Resolution in pixels per mm.')
@click.option('--shape', type=click.Choice(['rect', 'circle', 'heart']), default='rect',
              help='Shape of the lithophane.')
@click.option('--enhance/--no-enhance', default=False, help='Enhance image contrast before processing.')
def flat(input_path, output, width, height, max_thick, min_thick, frame_thick, frame_height, resolution, shape,
         enhance):
    """Generates a flat lithophane STL from an image.
    
    INPUT_PATH: Path to the source image file.
    """
    click.echo(f"Processing {input_path}...")

    try:
        # Generate the mesh
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
            shape=shape
        )

        # Determine output path
        if output is None:
            base, _ = os.path.splitext(input_path)
            output = f"{base}.stl"

        mesh_obj.save(output)
        click.echo(f"Success! STL saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', default=None, help='Output PNG file path.')
@click.option('--radius', '-r', default=100.0, help='Radius in mm.')
@click.option('--resolution', default=5, help='Resolution in pixels per mm.')
@click.option('--lines', default=30, help='Number of spiral lines.')
@click.option('--angle-step', default=0.05, help='Angle step for spiral.')
def spiral(input_path, output, radius, resolution, lines, angle_step):
    """Generates a spiral betty art image."""
    try:
        click.echo(f"Processing {input_path}...")

        result = generate_spiral_betty_png(
            image_path=input_path,
            radius_mm=radius,
            resolution=resolution,
            lines=lines,
            angle_step=angle_step
        )

        # Determine output path
        if output is None:
            base, _ = os.path.splitext(input_path)
            output = f"{base}_spiral.png"

        cv2.imwrite(output, result)
        click.echo(f"Success! Spiral art saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    cli()
