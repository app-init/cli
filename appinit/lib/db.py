from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from pytz import timezone

import pytz
import binascii
import os
import json
import hashlib

from appinit.lib.config import Settings

class Manager(object):
   
   __instance = None

   mongo_client = None
   host = None
   config = None
   settings = None
   db_host = None
   db_port = None

   __db = None

   def __new__(cls, *args, **kwargs):
      if Manager.__instance is None:
         Manager.__instance = object.__new__(cls)
         Manager.__instance.__set_class(*args, **kwargs)

      return Manager.__instance

   def __init__(self, db=None, new_client=False):
      self.setup(db)

   def __set_class(self, port=None, host=None):
      controller_path = os.path.dirname(os.path.realpath(__file__))
      base_path = os.path.abspath(os.path.join(controller_path, '../'))
      
      Manager.settings = Settings(path=base_path, verify=False)
      Manager.config = Manager.settings.get_config("mongodb")

      if Manager.config:
         port = None

         for k in Manager.config['container']['ports']:
            v = Manager.config['container']['ports'][k]
            
            if isinstance(v, int):
               port = v
               break

         if not port:
            port = 27017

         Manager.db_host = Manager.config['container']['name']
         Manager.db_port = port
      else:
         Manager.db_host = "mongodb"
         Manager.db_port = 27017 

      if "WEBPLATFORM_DEVEL" in os.environ:
         Manager.mongo_client = MongoClient("localhost", 27017, connect=False)
      else:
         Manager.mongo_client = MongoClient(Manager.db_host, Manager.db_port, connect=False)

   def setup(self, db):
      self.mongo_client = Manager.mongo_client
      self.host = Manager.host
      self.config = Manager.config
      self.settings = Manager.settings

      if db != None:
         self.__db = Manager.mongo_client[db]
      else:
         self.__db = Manager.mongo_client["appinit"]

   def db(self, db=None):
      if db == None:
         return self.__db
      else:
         return self.mongo_client[db]

   def new_connection(self):
      self.mongo_client = MongoClient(self.host, self.port)

   def drop_database(self, db):
      self.mongo_client.drop_database(db)

   def set_hostname(self, hostname):
      self.host = hostname
      Manager.host = hostname
      return hostname

   def get_hostname(self):
      return self.host

   def get_http_port(self):
      return self.http_port

   def get_user_uid(self):
      return self.session.user.get_uid()

   def get_user(self):
      return self.session.user.get()

   def parse_cursor_object(self, cursor):
      if cursor == None or cursor == "":
         return

      if "_id" in cursor.keys():
         _id = cursor['_id']
         del cursor['_id']
         cursor['id'] = _id

      return cursor

   def get_application(self, module=None, app=None):
      applications = self.settings.get_variable("applications-configs")

      if app is not None:
         for a in applications:
            if a['name'] == app:
               return a['title']

         return None
      else:
         if module == None:
            return applications

         for app in applications:
            if app['api']['name'] == module.split(".")[0]:
               return app['name']

         return "system"

   @staticmethod
   def get_current_time():
      return datetime.utcnow()

   @staticmethod
   def get_formatted_time():
      return Manager.get_current_time().isoformat()

   @staticmethod
   def timestamp_to_datetime(ts):
      return datetime.utcfromtimestamp(ts)

   @staticmethod
   def local_to_utc(date, local_tz):
      tz = timezone(local_tz)
      aware = tz.localize(date)

      return pytz.utc.normalize(aware)

   @staticmethod
   def local_timestamp_to_datetime(ts):
      date = datetime.fromtimestamp(ts)

      return Manager.local_to_utc(date, 'US/Eastern')

   def utc_to_local(date, tz):
      local_tz = pytz.timezone(tz)
      local_date = date.replace(tzinfo=pytz.utc).astimezone(local_tz)

      return local_tz.normalize(local_date)
