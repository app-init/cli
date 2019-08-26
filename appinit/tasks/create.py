from containers import main
import os, importlib, appinit 

def container(client, network, service):
   base_path = main.base_path
   settings = main.settings.get_config(service)
   prefix = main.settings.get_variable("docker-prefix")
   apps_path = main.settings.get_variable("apps-path")

   name = "%s-%s" % (prefix, service)
   num_cores = main.settings.get_num_cores(service, get_range=True)

   environment = main.get_environment(service)

   volumes = {
      "%s/docker/actions/%s" % (base_path, service): {
         "bind": "/home/container/actions",
         "mode": "rw",
      },
      "%s/data/%s" % (base_path, service): {
         "bind": "/home/container/data",
         "mode": "rw",
      },
      "%s/docker/%s" % (base_path, service): {
         "bind": "/home/container/config",
         "mode": "rw",
      },
      "%s" % os.path.dirname(appinit.__file__): {
         "bind": "/home/container/appinit",
         "mode": "rw",
      },
      "%s" % apps_path: {
         "bind": "/home/container/applications",
         "mode": "rw",
      },
   }

   if "volumes" in settings['container']:
      for key, value in settings['container']['volumes'].items():
         found = False
         path = None
         
         try:
            if "package" in value:
               if value['type'] == "python":
                  try:
                     module = importlib.import_module(value['package'])
                     
                     found = True
                     if "__init__" in module.__file__:
                        path = os.path.abspath(module.__file__ + '/../') # Have to go back one directory when modules are imported via __init__ 
                     else:
                        path = module.__file__ 

                  except ModuleNotFoundError:
                     print("Package you are trying to map to service volume doesn't exist. Skipping volume")

               else:
                  print("Current only support package type 'python' for service volume. Skipping volume.")

            else:
               path = value
               found = True
            
            if found:
               volumes[path] = {
                  "bind": "/home/container/%s" % key,
                  "mode": "rw"
               }
         
         except KeyError:
            print("You didn't specify a package type.\nCurrent only support package type 'python' for service volume. Skipping volume.")
            continue

   volumes = main.add_volumes(volumes)

   kwargs = {
      **settings['container'],
      "image": "%s-base:latest" % prefix,
      "hostname": service,
      "tty": True,
      "environment": environment,
      "name": name,
      "volumes": volumes,
      "command": "/home/container/actions/entry.sh",
   }

   if num_cores != None:
      kwargs['cpuset_cpus'] = num_cores

   container = client.containers.create(**kwargs)
   network.connect(container, aliases=[service])

   return container