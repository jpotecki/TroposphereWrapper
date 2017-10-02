from .helpers import checkForNoneValues
from troposphere import Parameter, Ref, Template, Sub, GetAtt
from troposphere.iam import Role
import troposphere.s3 as s3
from troposphere.codepipeline import (
  Pipeline, Stages, Actions, ActionTypeID, OutputArtifacts, InputArtifacts,
  ArtifactStore, DisableInboundStageTransitions)

from enum import Enum

class PipelineBuilder:
  def __init__(self):
    self._name: str = None
    self._stages: list = []
    self._artStorage: ArtifactStore = None
    self._codePipelineServiceRole: Role = None
    self._disableInboundStageTransitions: list = []
  
  def addDisableInboundStageTrans(self, dist: DisableInboundStageTransitions):
    self._disableInboundStageTransitions.append(dist)
    return self

  def setName(self, name: str):
    self._name = name
    return self

  def setArtStorage(self, store: ArtifactStore):
    self._artStorage = store
    return self
  
  def setCodePipelineServiceRole(self, role: Role):
    self._codePipelineServiceRole = role
    return self

  def addStage(self, stage: Stages):
    self._stages.append(stage)
    return self

  def build(self) -> Pipeline:
    checkForNoneValues(self)
    return Pipeline( 
        self._name
      , RoleArn = GetAtt(self._codePipelineServiceRole, "Arn")
      , Stages = self._stages
      , ArtifactStore = self._artStorage
      , DisableInboundStageTransitions = self._disableInboundStageTransitions
      )



class CodePipelineDISTBuilder:
  def __init__(self):
    self._stage: Stages = None
    self._reason: str = None
  
  def setStage(self, stage: Stages):
    self._stage = stage.Name
    return self

  def setReason(self, reason: str):
    self._reason = reason
    return self

  def build(self) -> DisableInboundStageTransitions:
    checkForNoneValues(self)
    return DisableInboundStageTransitions(
        StageName = self._stage
      , Reason = self._reason
      )

class CodePipelineArtifactStore:
  def __init__(self):
    self._type: str = None
    self._location: str = None

  def setS3Bucket(self, s3bucket: s3.Bucket):
    self.setType("S3").setLocation(Ref(s3bucket))
    return self

  def setType(self, type: str):
    self._type = type
    return self

  def setLocation(self, location: str):
    self._location = location
    return self

  def build(self) -> ArtifactStore:
    checkForNoneValues(self)
    return ArtifactStore( Type = self._type, Location = self._location)


class CodePipelineStageBuilder:
  def __init__(self):
    self._name: str = None
    self._actions: List[Actions] = []
  
  def setName(self, name: str):
    self._name = name
    return self

  def addAction(self, action: Actions):
    self._actions.append(action)
    return self

  def build(self) -> Stages:
    checkForNoneValues(self)
    return Stages( Name = self._name
                 , Actions = self._actions
                 )



class CodePipelineActionBuilder:
  def __init__(self):
    self._name: str = None
    self._actionType: ActionTypeID = None
    self._output: OutputArtifacts = []
    self._input: InputArtifacts = []
    self._runOrder: str = "1"
    self._configuration: dict = {}


  def setName(self, name: str):
      self._name = name
      return self

  def setActionType(self, at: ActionTypeID):
      self._actionType = at
      return self

  def addOutput(self, out: OutputArtifacts):
      self._output.append(out)
      return self

  def addInput(self, input: InputArtifacts):
      self._input.append(input)
      return self

  def setRunOrder(self, runOrder: str):
      self._runOrder = runOrder
      return self
  def setConfiguration(self, config: dict):
      self._configuration = config
      return self

  def build(self) -> Actions:
      checkForNoneValues(self)
      return Actions( Name = Sub(self._name + "-${AWS::StackName}")
                    , ActionTypeId = self._actionType
                    , OutputArtifacts = self._output
                    , InputArtifacts = self._input
                    , RunOrder = self._runOrder
                    , Configuration = self._configuration
                    )



class ActionIdOwner(Enum):
  AWS = (0, "AWS")
  ThirdParty = (1, "ThirdParty")
  Custom = (2, "Custom")
  def __str__(self):
    return self.value[1]

class ActionIdCategory(Enum):
  Invoke = (0, "Invoke")  
  Source = (1, "Source")
  Approval = (2, "Approval")
  Build = (3, "Build")
  Deploy = (4, "Deploy")
  Test = (5, "Test")
  def __str__(self):
    return self.value[1]

class CodePipelineActionTypeIdBuilder:
  def __init__(self):
    self._category: ActionIdCategory = None
    self._owner: ActionIdOwner = None
    self._version: str = "1"
    self._provider: str = None

  def setCategory(self, cat: ActionIdCategory):
    self._category = cat
    return self

  def setOwner(self, owner: ActionIdOwner):
    self._owner = owner
    return self

  def setVersion(self, version: str):
    self._version = version
    return self

  def setProvider(self, prov: str):
    self._provider = prov
    return self

  def setCodeCommitSource(self, version: str):
    self.setCategory(ActionIdCategory.Source) \
        .setOwner(ActionIdOwner.AWS) \
        .setVersion(version) \
        .setProvider("CodeCommit")
    return self

  def setCodeBuildSource(self, version: str):
    self.setCategory(ActionIdCategory.Build) \
        .setOwner(ActionIdOwner.AWS) \
        .setVersion(version) \
        .setProvider("CodeBuild")
    return self

  def build(self) -> ActionTypeID:
    checkForNoneValues(self)
    return ActionTypeID( Category = str(self._category)
                       , Owner = str(self._owner)
                       , Version = self._version
                       , Provider = self._provider
                       )


class StageBuilderHelper:
  def _getStageNameWithoutStackNameRef(self, stage: Stages)-> str:
    name = stage.Name
    name = name.replace("-${AWS::StackName}", "")
    return name[0].upper() + name[1:]

  def getManualApprovalStageNoNotification( self
                                          , stage: Stages
                                          , version: str = "1"
                                          ) -> Stages:
    actionId = CodePipelineActionTypeIdBuilder() \
      .setCategory(ActionIdCategory.Approval) \
      .setOwner(ActionIdOwner.AWS) \
      .setVersion(version) \
      .setProvider("Manual") \
      .build()
    
    name = stage.Name
    action = CodePipelineActionBuilder() \
      .setActionType(actionId) \
      .setName("ManualApprovalActionFor" + name) \
      .build()

    return CodePipelineStageBuilder() \
      .setName(name + "-Approval") \
      .addAction(action) \
      .build()




# example
def exampleSourceStage(repo: str, branch: str) -> Stages:
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

def getExample() -> str:
  sourceStage = exampleSourceStage("user/exampleRepoName", "master")
  disableInbound = CodePipelineDISTBuilder() \
    .setReason("Disabling transition until tests are completed") \
    .setStage(sourceStage) \
    .build()

  pipeline = PipelineBuilder() \
    .addDisableInboundStageTrans(disableInbound) \
    .addStage(sourceStage) \
    .build()

  t = Template()
  t.add_resource(pipeline)

  return t.to_json()