from .helpers import checkForNoneValues
from troposphere.codebuild import Source, Environment, Artifacts, Project
from troposphere import Sub, Template

class CodeBuildBuilder:
  def __init__(self):
    self._env: Environment = None
    self._source: Source = None
    self._artifacts: Artifacts = None
    self._name: str = None
    self._serviceRole: str = None

  def setEnvironment(self, env: Environment):
    self._env = env
    return self
  
  def setSource(self, source: Source):
    self._source = source
    return self
  
  def setArtifacts(self, artifacts: Artifacts):
    self._artifacts = artifacts
    return self
  
  def setName(self, name: str):
    self._name = name
    return self
  
  def setServiceRole(self, serviceRole: str):
    self._serviceRole = serviceRole
    return self
  
  def build(self) -> Project:
    checkForNoneValues(self)
    return Project( self._name
                  , Name = Sub(self._name + "-${AWS::StackName}")
                  , Environment = self._env
                  , Source = self._source
                  , Artifacts = self._artifacts
                  , ServiceRole = self._serviceRole
                  )

class CodeBuildEnvBuilder:
  def __init__(self):
    self._compType: str = None
    self._image: str = None
    self._type: str = None
    self._envVars: list = []
  
  def setComputeType(self, compType: str):
    self._compType = compType
    return self
  
  def setImage(self, image: str):
    self._image = image
    return self

  def setType(self, type: str):
    self._type = type
    return self

  def addEnvVars(self, envVars: dict):
    self._envVars.append(envVars)
    return self
  
  def build(self) -> Environment:
    checkForNoneValues(self)
    return Environment( ComputeType = self._compType
                      , Image = self._image
                      , Type = self._type
                      , EnvironmentVariables = self._envVars
                      )

class CodeBuildSourceBuilder:
  def __init__(self):
    self._type: str = None
    self._buildSpec: str = None

  def setType(self, type: str):
    self._type = type
    return self

  def setBuildSpec(self, buildSpec: str):
    self._buildSpec = buildSpec
    return self

  def build(self) -> Source:
    checkForNoneValues(self)
    return Source( Type = self._type
                 , BuildSpec = self._buildSpec
                 )

class CodeBuildArtifactsBuilder:
  def __init__(self):
    self._type: str = None

  def setType(self, type: str):
    self._type = type.upper()
    return self

  def build(self) -> Artifacts:
    checkForNoneValues(self)
    return Artifacts( Type = self._type )


# examples
def exampleCodeSpec():
  return "version: 0.2\n" \
           "\n" \
           "phases:\n" \
           "\t" "build:\n" \
           "\t\t" "commands:\n" \
           "\t\t\t" "- elm-make Main.elm --yes\n" \
           "artifacts:\n" \
           "\t" "files:\n" \
           "\t\t" "- index.html"

def getExample() -> str:

  name = "ExampleElmAppBuilder"

  env = CodeBuildEnvBuilder() \
      .setComputeType("BUILD_GENERAL1_SMALL") \
      .setImage("emmanuelrosa/elm-base") \
      .setType("LINUX_CONTAINER") \
      .addEnvVars( { "Name": "APP_NAME", "Value": name } ) \
      .build()

  source = CodeBuildSourceBuilder() \
      .setType("CodePipeline") \
      .setBuildSpec(exampleCodeSpec()) \
      .build()

  artifacts = CodeBuildArtifactsBuilder() \
      .setType("CodePipeline") \
      .build()
  
  codeBuild = CodeBuildBuilder() \
      .setArtifacts(artifacts) \
      .setEnvironment(env) \
      .setSource(source) \
      .setName(name) \
      .setServiceRole("arn::blabla") \
      .build()
  
  t = Template()
  t.add_resource(codeBuild)

  return t.to_json()
