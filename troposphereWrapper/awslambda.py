from troposphere.awslambda import Function, Code, MEMORY_VALUES, Environment
from troposphere.iam import Role
from troposphere import Join, Ref, GetAtt, Sub

from enum import Enum
from typing import List

from .helpers import checkForNoneValues

class LambdaRuntime(Enum):
  Python3x = (1, "python3.6")
  Python2x = (2, "python2.7")
  Node6x   = (3, "nodejs6.10")
  def __str__(self):
    return self.value[1]

class LambdaBuilder:
  def __init__(self):
    self._name: str = None
    self._code: Code = None
    self._handler: str = None
    self._role: Role = None
    self._runtime: LambdaRuntime = None
    self._memory: int = 128
    self._envVars: dict = {}

  def setName(self, name: str):
    self._name = name
    return self

  def addEnvironmentVariable(self, key: str, value: str):
    self._envVars[key] = value
    return self

  def setSourceCode(self, code: List[str]):
    self._code = Code( ZipFile = Join("", code) )
    return self

  def setHandler(self, handler: str):
    self._handler = handler
    return self

  def setRole(self, role: Role):
    self._role = role
    return self
  
  def setRuntime(self, runtime: LambdaRuntime):
    self._runtime = runtime
    return self

  def setMemory(self, memory: int):
    self._memory = memory
    return self

  def build(self) -> Function:
    checkForNoneValues(self)
    return Function(
        self._name
      , Code = self._code
      , Handler = self._handler
      , FunctionName = Sub(self._name + "${AWS::StackName}")
      , MemorySize = self._memory
      , Role = GetAtt(self._role, "Arn")
      , Runtime = str(self._runtime)
      , Environment = Environment( Variables = self._envVars)
      )
