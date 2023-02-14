"""CLI for acquiring data using Kinect Azure
"""

import os
import click
from azure_acquire.util import start_recording_RT

orig_init = click.core.Option.__init__

def new_init(self, *args, **kargs):
    orig_init(self, *args,  **kargs)
    self.show_default = True

click.core.Option.__init__ = new_init

@click.group()
@click.version_option()
def cli():
    pass

@cli.command(name="record", help='start recording depth and IR video')
@click.argument('base-dir', type=click.Path(exists=True, resolve_path=False))
@click.option('--ses')