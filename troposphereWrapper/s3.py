from troposphere.s3 import *

from .helpers import *
from enum import Enum

class S3Access(Enum):
  Private = (1, "Private")
  PublicRead = (2, "PublicRead")
  PublicReadWrite = (3, "PublicReadWrite")
  AuthenticatedRead = (4, "AuthenticatedRead")
  BucketOwnerRead = (5, "BucketOwnerRead")
  BucketOwnerFullControl = (6, "BucketOwnerFullControl")
  LogDeliveryWrite = (7, "LogDeliveryWrite")
  def __str__(self):
    return self.value[1]



class S3Builder:
  def __init__(self):
    self._name = None
    self._access = None

  def setName(self, name: str):
    self._name = name
    return self

  def setAccess(self, access: S3Access):
    self._access = access
    return self

  def build(self) -> Bucket:
    return Bucket( 
        self._name
      , AccessControl = self._access
      )


class S3StaticWebsiteBuilder(S3Builder):
  def __init__(self):
    super().__init__()
    self._indexDoc: str = "index.html"

  def build(self):
    webConf = WebsiteConfiguration(
        IndexDocument = self._indexDoc
      )
    return Bucket(
        self._name
      , AccessControl = str(self._access)
      , WebsiteConfiguration = webConf
    )
