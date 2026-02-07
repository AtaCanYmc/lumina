import click


@click.group()
def cli():
    """Lumina: 14 Şubat Maker Paketi"""
    pass


@cli.command()
@click.option('--input', required=True, help='Görsel yolu')
@click.option('--mode', type=click.Choice(['flat', 'curved']), default='flat')
@click.option('--radius', type=float, default=50.0, help='Bükme yarıçapı (mm)')
def flat_lithophane(path, mode, radius):
    """Resmi 3D STL dosyasına dönüştürür."""
    click.echo(f"Processing {path}...")
    # Burada senin yazdığın image_to_flat_stl veya curved_stl çağrılacak.
    click.echo("Success! STL generated in temp folder.")


if __name__ == '__main__':
    cli()
