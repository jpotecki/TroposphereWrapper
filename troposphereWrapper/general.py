from troposphere import Parameter, Template
from .helpers import checkForNoneValues

class ParameterBuilder:
  def __init__(self):
    self._name: str = None
    self._description: str = None
    self._type: str = None

  def setName(self, name: str):
    self._name = name
    return self

  def setDescription(self, description: str):
    self._description = description
    return self

  def setType(self, type: str):
    self._type = type
    return self
  
  def build(self) -> Parameter:
    checkForNoneValues(self)
    return Parameter(self._name
      , Description = self._description
      , Type = self._type
      )

def getExample() -> str:
  template = Template()
  template.add_parameter(
    ParameterBuilder() \
      .setName( "DeployLambdaFunction") \
      .setDescription("Lambda Function Name to run in Deploy Stage") \
      .setType("String") \
      .build()
    )
  return template.to_json()
