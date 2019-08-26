from containers import main
from docker import APIClient
import os, appinit 

client = APIClient(base_url="unix://var/run/docker.sock")

def run(service, force=False):
   path = os.path.dirname(appinit.__file__)
   prefix = main.settings.get_variable("docker-prefix")
   
   image_name = '%s-base:latest' % prefix

   print("Building base image.")
   kwargs = {
      'nocache': force,
      'decode': True,
      'forcerm': True,
      'path': path + "/docker/base/",
      'dockerfile': path + "/docker/base/Dockerfile",
      'rm': True,
      'tag': image_name,
   }
   for line in client.build(**kwargs):
      if "stream" in line: print(line['stream'])
   print("Done -- building base image.")
