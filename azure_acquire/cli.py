"""
CLI for acquiring data using Kinect Azure
"""

import os
import click
from azure_acquire.util import start_recording_RT

orig_init = click.core.Option.__init__

def new_init(self, *args, **kwargs):
    orig_init(self, *args, **kwargs)
    self.show_default = True

click.core.Option.__init__ = new_init

@click.group()
@click.version_option()
def cli():
    pass

@cli.command(name="record", help='start recording depth and IR video')
@click.argument('base-dir', type=click.Path(exists=True, resolve_path=False))
@click.option('--subject-name', help='subject name of the recording')
@click.option('--session-name', help='session name of the recording')
@click.option('--recording-length', '-t', type=float, default = 30, help="recording time (minutes)")
@click.option('--preview', is_flag=True,
              help='show frame preview during recording')
@click.option('--display-time', is_flag=True,
              help='show time during the recording')
def record(base_dir, subject_name, session_name, recording_length, preview, display_time):
    #change recording time from minutes to seconds
    recording_length = recording_length * 60

    start_recording_RT(base_dir=base_dir, subject_name = subject_name, 
                       session_name = session_name, recording_length = recording_length, 
                       display_frames = preview, display_time = display_time)

if __name__ == '__main__':
    cli()