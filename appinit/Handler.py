import os, sys, docker, json, shutil

class CLI(object):
   def __init__(self, settings, debug, force):
      self.settings = settings

      self.debug = debug
      self.force = force

      self.options = {
         "debug": self.debug,
         "force": self.force,
      }

      self.client = docker.DockerClient(base_url="unix://var/run/docker.sock")
      self.services = self.settings.get_service()
      self.base_path = settings.get_path()

   def parse_args(self, command, params):
      #only run setup and install, others have yet to be implemented 
      if command == "setup":
         method = getattr(self, command, None)()
     
      elif command == "config":
         method = getattr(self, command, None)(**params)
      
      elif command == "variables":
         self.parse_variables(**params)
      
      elif command == "routes":
         self.parse_routes(**params)
     
      elif command in ["start", "restart", "stop", "update", "reset"]:
         if len(params) > 0:
            for i in params:
               self.run_container(service=i, action=command)
         else:
            self.run_container(action=command)
      elif command == 'run':
         self.run_command(params['params'])

   def run_command(self, service):
      from Docker import ContainerHandler
      
      container = ContainerHandler(self.settings, self.client, self.options)
      container.run_command(service)

   def run_container(self, service=None, action=None):
      from Docker import ContainerHandler
      
      container = ContainerHandler(self.settings, self.client, self.options)
      if service == None:
         if action == "run":
            print("You must specify a service you'd like to run or a command to be run.")
         else:
            container.run(action)
      else:
         if action == "run":
            container.run_command(service)
         else:
            container.run_service(service, action)

   def config(self, command, service, path=None, config=None, default=False):
      from lib.config import Settings
      
      if command in "get":
         config = self.settings.get_config(service)
         print(json.dumps(config, indent=2))
         sys.exit(1)
         
      
      try:
         if not default:
            if config == None:
               config = json.load(open(path))

      except IsADirectoryError:
         print("The value you specified for '--config' is a directory. This value but be a JSON file")
      except TypeError as e:
         print("The config you specified is not valid JSON")
      finally:
         config_path = "%s/settings/%s.json" % (self.base_path, service)
         default_path = "%s/settings/default-%s.json" % (self.base_path, service)
         
         config_target = open(config_path, "w")

         if not os.path.isfile(default_path):
            default_target = open(default_path, "w+")
            default_target.write(json.dumps(self.settings.get_config(service), indent=2))
            default_target.close()

         if not default:
            config_target.write(json.dumps(config, indent=2))
         else:
            config = json.load(open(default_path))
            config_target.write(json.dumps(config, indent=2))

         config_target.close()

      self.settings = Settings(path=self.base_path)

   def parse_variables(self, command=None, variable=None, value=None, default=False):
      config = self.settings.get_config("variables")

      current_value = self.settings.get_variable(variable)
      if current_value == None:
         sys.exit(1)

      if command == "get":
         print(current_value)
         sys.exit(1)

      if not default:
         if "," in value:
            config[variable] = value.strip().split(",")
         else:
            config[variable] = value

      self.config("set", "variables", config=config, default=default)
   
   def parse_routes(self, command=None, route=None, default=False):
      config = self.settings.get_config("variables")
      routes = self.settings.get_variable("routes")
      routes_path = self.settings.get_variable("routes-path")
      route_configs = self.settings.get_variable("route-configs")

      if len(routes) == 0 and command in ["list", "enable", "disable", "remove"]:
         print("Currently not tracking any routes.\nPlease add a route if you'd like to run '%s'" % command)
         sys.exit(1)

      if route in routes and command == "add":
         print("Route '%s' is currently already being tracked." % route)
         sys.exit(1)

      if command == "add":
         if "," in route:
            routs += route.strip().split(",")
         else:
            routes.append(route)

         route_config, error = self.settings.find_route(route)
         if error is not None:
            if error == "json parse error":
               print("Error parsing `route.json` for route `%s`" % route)
            elif error == "route no config":
               print("Route `%s` doesn't have a `route.json` file." % route)
            elif error == "no route dir":
               print("Route '%s' isn't a directory in `routes-path` (%s) variable." % (route, config['routes-path']))

            sys.exit(1)
         else:
            # Relative paths used in app.json configs.
            # Need to add those relative paths based on apps-path variable
            if 'frontend' in route_config:
               route_config['frontend']['path'] = os.path.join(routes_path, route, route_config['frontend']['path'])
            
            route_config['api']['path'] = os.path.join(routes_path, route, route_config['api']['path'])
            route_config['route-dir-name'] = route
            route_config['active'] = True
            route_configs.append(route_config)

            self.parse_variables(command="set", variable="routes", value=routes)
            self.parse_variables(command="set", variable="route-configs", value=route_configs)

         print(",".join(routes))

      elif command == "list":
         print(",".join(current_value))
         sys.exit(1)
      
      elif command in ["enable", "disable"]:
         new_route_configs = []
         for route_config in route_configs:
            if route_config['route-dir-name'] == route:
               route_config['active'] = command == "enable"
            
            new_route_configs.append(route_config)

         self.parse_variables(command="set", variable="route-configs", value=new_route_configs)

      elif command == "remove":
         if route not in routes:
            print("Route requested '%s' to remove doesn't exist" % route)
         else:
            new_route_configs = [i for i in route_configs if i['route-dir-name'] != route]
            new_routes = [i for i in routes if i != route]

            self.parse_variables(command="set", variable="routes", value=new_routes)
            self.parse_variables(command="set", variable="route-configs", value=new_route_configs)
   
   def setup(self):
      from tasks import build

      build.run("mongodb", force=self.options['force'])

   def tail(self, service, follow=False):
      pass