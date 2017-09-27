from .helpers import checkForNoneValues
from troposphere import Parameter, Ref, Template, Sub
from troposphere.codepipeline import (
  Pipeline, Stages, Actions, ActionTypeID, OutputArtifacts, InputArtifacts,
  ArtifactStore, DisableInboundStageTransitions)

class PipelineBuilder:
  def __init__(self):
    self._name = None
    self._stages = []
    self._artStorage = None
    self._codePipelineServiceRole = None
  
  def setName(self, name):
    self._name = name
    return self

  def setArtStorage(self, s3):
    self._artStorage = s3
    return self
  
  def setCodePipelineServiceRole(self, role):
    self._codePipelineServiceRole = role
    return self

  def addStage(self, stage):
    self._stages.append(stage)
    return self

  def build(self):
    checkForNoneValues(self)
    return Pipeline( 
              self._name
            , RoleArn = Ref(self._codePipelineServiceRole)
            , Stages = self._stages
            , ArtifactStore = 
                ArtifactStore( Type="S3"
                             , Location = Ref(self._artStorage)
                             )
            , DisableInboundStageTransitions = [
              DisableInboundStageTransitions( 
                  StageName="CopyToS3HtmlToS3"
                , Reason = "Disabling transition until tests are completed"
                )
              ]
    )



class CodePipelineStageBuilder:
  def __init__(self):
    self._name = None
    self._actions = []
  
  def setName(self, name):
    self._name = name
    return self

  def addAction(self, action):
    self._actions.append(action)
    return self

  def build(self):
    checkForNoneValues(self)
    return Stages( Name = self._name, Actions = self._actions)



class CodePipelineActionBuilder:
  def __init__(self):
    self._name = None
    self._actionType = None
    self._output = []
    self._input = []
    self._runOrder = "1"
    self._configuration = {}


  def setName(self, name):
      self._name = name
      return self

  def setActionType(self, at):
      self._actionType = at
      return self

  def addOutput(self, out):
      self._output.append(out)
      return self

  def addInput(self, input):
      self._input.append(input)
      return self

  def setRunOrder(self, runOrder):
      self._runOrder = runOrder
      return self
  def setConfiguration(self, config):
      self._configuration = config
      return self

  def build(self):
      checkForNoneValues(self)
      return Actions( Name = self._name
                    , ActionTypeId = self._actionType
                    , OutputArtifacts = self._output
                    , InputArtifacts = self._input
                    , RunOrder = self._runOrder
                    , Configuration = self._configuration
                    )



class CodePipelineActionTypeIdBuilder:
  def __init__(self):
    self._category = None
    self._owner = None
    self._version = None
    self._provider = None

  def setCategory(self, cat):
    self._category = cat
    return self

  def setOwner(self, owner):
    self._owner = owner
    return self

  def setVersion(self, version):
    self._version = version
    return self

  def setProvider(self, prov):
    self._provider = prov
    return self

  def setCodeCommitSource(self, version):
    self.setCategory("Source") \
        .setOwner("AWS") \
        .setVersion(version) \
        .setProvider("CodeCommit")
    return self

  def setCodeBuildSource(self, version):
    self.setCategory("Build") \
        .setOwner("AWS") \
        .setVersion(version) \
        .setProvider("CodeBuild")
    return self

  def build(self):
    checkForNoneValues(self)
    return ActionTypeID( Category = self._category
                       , Owner = self._owner
                       , Version = self._version
                       , Provider = self._provider
                       )



# example
def exampleSourceStage(repo, branch):
  actionid = CodePipelineActionTypeIdBuilder() \
      .setCodeCommitSource("1") \
      .name("ExampleSourceActionId") \
      .build()
  
  action = CodePipelineActionBuilder() \
      .setName("ExampleSourceAction") \
      .setConfiguration({"BranchName" : branch, "RepositoryName" : repo}) \
      .setActionType(actionid) \
      .addOutput(OutputArtifacts(Name="ElmCodeOutput")) \
      .build()

  return CodePipelineStageBuilder() \
      .setName("ExampleSourceStage") \
      .addAction(action) \
      .build()

if __name__ == "__main__":
  pipeline = PipelineBuilder() \
    .addStage(exampleSourceStage("user/exampleRepoName", "master")) \
    .build()
  
  t = Template()
  t.add_resource(pipeline)
  print(t.to_json())