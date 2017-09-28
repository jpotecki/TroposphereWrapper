from troposphere import Template, Ref
from troposphere.iam import Role, InstanceProfile

import awacs.aws
import awacs.s3
import awacs.codecommit
import awacs.codedeploy
import awacs.codebuild
import awacs.elasticbeanstalk
import awacs.ec2
import awacs.elasticloadbalancing
import awacs.autoscaling
import awacs.sns
import awacs.cloudwatch
import awacs.cloudformation
import awacs.rds
import awacs.sqs
import awacs.ecs
import awacs.iam
import awacs.awslambda
import awacs.opsworks
from awacs.aws import Action

from .helpers import checkForNoneValues
from typing import List
from enum import Enum


class Effects(Enum):
  Allow   = (1, awacs.aws.Allow)
  Deny    = (2, awacs.aws.Deny)
  def __str__(self):
    return str(self.value[1])
  def get(self):
    return self.value[1]

class RoleBuilder:
  def __init__(self):
    self._name: str = None
    self._policy: awacs.aws.Policy = None
  
  def setName(self, name: str):
    self._name = name
    return self

  def setPolicy(self, policy: awacs.aws.Policy):
    self._policy = policy
    return self

  def build(self) -> Role:
    checkForNoneValues(self)
    return Role(
        self._name
      , AssumeRolePolicyDocument = self._policy
      )

class RoleBuilderHelper:
  def oneClickCodePipeServicePolicy(self) -> List[awacs.aws.Policy]:
    statements = [
        awacs.aws.Statement(
          Action = [ awacs.s3.GetObject
                   , awacs.s3.GetObjectVersion
                   , awacs.s3.GetBucketVersioning
                   ]
        , Resource = [ "*" ]
        , Effect = awacs.aws.Allow
        )
     , awacs.aws.Statement(
          Action = [ awacs.s3.PutObject ]
        , Resource = [ "arn:aws:s3:::codepipeline*" 
                     , "arn:aws:s3:::elasticbeanstalk*"
                     ]
        , Effect = awacs.aws.Allow
        )
     , awacs.aws.Statement(
          Action = [ awacs.codecommit.CancelUploadArchive
                   , awacs.codecommit.GetBranch
                   , awacs.codecommit.GetCommit
                   , awacs.codecommit.GetUploadArchiveStatus
                   , awacs.codecommit.UploadArchive
                   ]
        , Resource = [ "*" ]
        , Effect = awacs.aws.Allow
        )
    , awacs.aws.Statement(
        Action = [ awacs.codedeploy.CreateDeployment
                 , awacs.codedeploy.GetApplicationRevision
                 , awacs.codedeploy.GetDeployment
                 , awacs.codedeploy.GetDeploymentConfig
                 , awacs.codedeploy.RegisterApplicationRevision
                 ]
      , Resource = [ "*" ]
      , Effect = awacs.aws.Allow
      )
    , awacs.aws.Statement(
        Action = [ awacs.elasticbeanstalk.Action("*")
                 , awacs.ec2.Action("*")
                 , awacs.elasticloadbalancing.Action("*")
                 , awacs.autoscaling.Action("*")
                 , awacs.cloudwatch.Action("*")
                 , awacs.s3.Action("*")
                 , awacs.sns.Action("*")
                 , awacs.cloudformation.Action("*")
                 , awacs.rds.Action("*")
                 , awacs.sqs.Action("*")
                 , awacs.ecs.Action("*")
                 , awacs.iam.PassRole
                 ]
      , Resource = [ "*" ]
      , Effect = awacs.aws.Allow
      )
    , awacs.aws.Statement(
        Action = [ awacs.awslambda.InvokeFunction
                 , awacs.awslambda.ListFunctions
                 ]
      , Resource = [ "*" ]
      , Effect = awacs.aws.Allow
      )
    , awacs.aws.Statement(
        Action = [ awacs.opsworks.CreateDeployment
                 , awacs.opsworks.DescribeApps
                 , awacs.opsworks.DescribeCommands
                 , awacs.opsworks.DescribeDeployments
                 , awacs.opsworks.DescribeInstances
                 , awacs.opsworks.DescribeStacks
                 , awacs.opsworks.UpdateApp
                 , awacs.opsworks.UpdateStack
                 ]
      , Resource = [ "*" ]
      , Effect = awacs.aws.Allow
      )
    , awacs.aws.Statement(
        Action = [ awacs.cloudformation.CreateStack
                 , awacs.cloudformation.DeleteStack
                 , awacs.cloudformation.DescribeStacks
                 , awacs.cloudformation.UpdateStack
                 , awacs.cloudformation.CreateChangeSet
                 , awacs.cloudformation.DeleteChangeSet
                 , awacs.cloudformation.DescribeChangeSet
                 , awacs.cloudformation.ExecuteChangeSet
                 , awacs.cloudformation.SetStackPolicy
                 , awacs.cloudformation.ValidateTemplate
                 , awacs.iam.PassRole
                 ]
      , Resource = [ "*" ]
      , Effect = awacs.aws.Allow
      )
    , awacs.aws.Statement(
        Action = [ awacs.codebuild.BatchGetBuilds
                 , awacs.codebuild.StartBuild
                 ]
      , Resource = [ "*" ]
      , Effect = awacs.aws.Allow
      )
    ]
    return awacs.aws.Policy(
        Statement = statements
      , Version = "2012-10-17"
      )


def getExample() -> str:
  t = Template()
  
  role = RoleBuilder() \
    .setName("ExamplePipelineRole") \
    .setPolicy(RoleBuilderHelper().oneClickCodePipeServicePolicy()) \
    .build()
  
  t.add_resource(role)
  return t.to_json()


