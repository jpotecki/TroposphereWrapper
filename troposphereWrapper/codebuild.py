from .helpers import checkForNoneValues
import troposphere.codebuild as cb
from troposphere import Sub, Template

class CodeBuildBuilder:
  def __init__(self):
    self._env = None
    self._source = None
    self._artifacts = None
    self._name = None
    self._serviceRole = None

  def setEnvironment(self, env):
    self._env = env
    return self
  
  def setSource(self, source):
    self._source = source
    return self
  
  def setArtifacts(self, artifacts):
    self._artifacts = artifacts
    return self
  
  def setName(self, name):
    self._name = name
    return self
  
  def setServiceRole(self, serviceRole):
    self._serviceRole = serviceRole
    return self
  
  def build(self):
    checkForNoneValues(self)
    return cb.Project( self._name
                     , Name = Sub(self._name + "-${AWS::StackName}")
                     , Environment = self._env
                     , Source = self._source
                     , Artifacts = self._artifacts
                     , ServiceRole = self._serviceRole
                     )

class CodeBuildEnvBuilder:
  def __init__(self):
    self._compType = None
    self._image = None
    self._type = None
    self._envVars = []
  
  def setComputeType(self, compType):
    self._compType = compType
    return self
  
  def setImage(self, image):
    self._image = image
    return self

  def setType(self, type):
    self._type = type
    return self

  def addEnvVars(self, envVars):
    self._envVars.append(envVars)
    return self
  
  def build(self):
    return cb.Environment( ComputeType = self._compType
                         , Image = self._image
                         , Type = self._type
                         , EnvironmentVariables = self._envVars
                         )

class CodeBuildSourceBuilder:
  def __init__(self):
    self._type = None
    self._buildSpec = None

  def setType(self, type):
    self._type = type
    return self

  def setBuildSpec(self, buildSpec):
    self._buildSpec = buildSpec
    return self

  def build(self):
    return cb.Source( Type = self._type
                    , BuildSpec = self._buildSpec
                    )

class CodeBuildArtifactsBuilder:
  def __init__(self):
    self._type = None

  def setType(self, type):
    self._type = type
    return self

  def build(self):
    return cb.Artifacts( Type = self._type )


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

if __name__ == "__main__":

  name = "ExampleElmAppBuilder"

  env = CodeBuildEnvBuilder() \
        .setComputeType("BUILD_GENERAL1_SMALL") \
        .setImage("emmanuelrosa/elm-base") \
        .setType("LINUX_CONTAINER") \
        .addEnvVars( { "Name": "APP_NAME", "Value": name } ) \
        .build()

  source = CodeBuildSourceBuilder() \
            .setType("CODEPIPELINE") \
            .setBuildSpec(exampleCodeSpec()) \
            .build()

  artifacts = CodeBuildArtifactsBuilder() \
            .setType("CODEPIPELINE") \
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
  print(t.to_json())
