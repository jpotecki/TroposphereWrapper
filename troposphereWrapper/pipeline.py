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

# example
def exampleSourceStage(repo, branch):
    return Stages(
      Name = "ElmSourceSourceCodeStage"
      , Actions = [ Actions( Name = "ElmSourceAction"
                  , ActionTypeId = ActionTypeID( Category = "Source"
                                               , Owner = "AWS"
                                               , Version = "1"
                                               , Provider = "CodeCommit" 
                                               )
                  , OutputArtifacts = [ OutputArtifacts(Name="ElmCodeOutput")]
                  , Configuration = { "BranchName": branch
                                    , "RepositoryName" : repo }
                  , RunOrder="1" ) ] 
    ) 

if __name__ == "__main__":
  pipeline = PipelineBuilder() \
    .addStage(exampleSourceStage("user/exampleRepoName", "master")) \
    .build()
  
  t = Template()
  t.add_resource(pipeline)
  print(t.to_json())