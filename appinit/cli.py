"""usage:
   appinit [ --force --debug  --base-path <base-path> ] <command> [<args>...]
   appinit (--version | --help)

Options:
   -h --help                Print this help message
   --version                Show version
   --base-path <base-path>  Specify a base path for all container 
                            setup to run off of
   -f --force               Force the action being preformed
   -d --debug               Enable controller debugging mode,
                            for controller development only

commands for the controller are:
   setup        Build containters
   update       *not finished* Local dependancy update
   start        Start
   stop         Stop
   restart      Restart
   reset        Reset
   config       Commands for setting or getting config
   variables    Commands for setting webplatform variables
   routes       Commands for interfacing with route configuration

See 'app-init' <command> -h' for more information on a specific command.
"""
import os
import sys

sys.dont_write_bytecode = True

commands = [
   "setup",
   "start",
   "stop",
   "restart",
   "variables",
   "routes",
   "config",
   "reset"
]

def main():
   controller_path = os.path.dirname(os.path.realpath(__file__))
   base_path = None

   try:
      from webplatform_cli import base_path
   except:
      base_path = os.path.abspath(os.path.join(controller_path))
   finally:
      if base_path not in sys.path:
         sys.path.append(base_path)
      
      if controller_path not in sys.path:
         sys.path.append(controller_path)

   from lib.config import Settings
   from docopt import docopt

   args = docopt(__doc__,
               version='App Init CLI Version 1.0.3',
               options_first=True)

   if not args['<command>'] in commands:
      sys.stderr.write(__doc__)
      sys.exit(1)

   if args['--base-path']:
      base_path = os.path.abspath(os.path.join(args['--base-path']))

   settings = Settings(path=base_path)

   from Handler import CLI
   import Parser

   options = {
      'debug': args['--debug'],
      'force': args['--force'],
   }

   ctrl = Parser.parser(args['<command>'], args['<args>'], **options)
   
   controller = CLI(settings, **options)
   controller.parse_args(**ctrl)

if __name__ == "__main__":
   main()