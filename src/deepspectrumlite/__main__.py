#                               DeepSpectrumLite
# ==============================================================================
# Copyright (C) 2020-2021 Shahin Amiriparian, Tobias Hübner, Maurice Gerczuk,
# Sandra Ottl, Björn Schuller: University of Augsburg. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ==============================================================================
import sys, os

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

import click
import logging
import logging.config
import pkg_resources

from deepspectrumlite.cli.train import train
from deepspectrumlite.cli.utils import add_options
from deepspectrumlite import __version__ as VERSION



_global_options = [
    click.option('-v', '--verbose', count=True),
]


version_str = f"DeepSpectrumLite %(version)s\nCopyright (C) 2020-2021 Shahin Amiriparian, Tobias Hübner, Maurice Gerczuk, Sandra Ottl, " \
                      "Björn Schuller\n" \
                      "License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.\n" \
                      "This is free software: you are free to change and redistribute it.\n" \
                      "There is NO WARRANTY, to the extent permitted by law."

@click.group()
@add_options(_global_options)
@click.version_option(VERSION, message=version_str)
def cli(verbose):
    click.echo('Verbosity: %s' % verbose)
    log_levels = ['ERROR', 'INFO', 'DEBUG']
    verbose = min(2, verbose)
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,  # this fixes the problem
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': log_levels[verbose],
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_levels[verbose],
                'propagate': True
            }
        }
    })


cli.add_command(train)