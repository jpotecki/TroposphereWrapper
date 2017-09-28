from troposphere import Template, Ref, Sub
from troposphere.iam import Role, InstanceProfile, Policy

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
import awacs.sts
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
    self._policy: List[Policy] = []
    self._assumePolicy: awacs.aws.Policy = None
  
  def setName(self, name: str):
    self._name = name
    return self

  def setAssumePolicy(self, assume: awacs.aws.Policy):
    self._assumePolicy = assume
    return self

  def addPolicy(self, policy: Policy):
    self._policy.append(policy)
    return self

  def build(self) -> Role:
    checkForNoneValues(self)
    return Role(
        self._name
      , RoleName = Sub(self._name+"-${AWS::StackName}")
      , AssumeRolePolicyDocument = self._assumePolicy
      , Policies = self._policy
      )



class StatementBuilder:
  def __init__(self):
    self._principal: awacs.aws.Principal = None
    self._actions: List[ awacs.aws.Action] = []
    self._effect: Effects = None
    self._resource: List[str] = []

  def addResource(self, res: str):
    self._resource.append(res)
    return self

  def setPrincipal(self, principal: awacs.aws.Principal):
    self._principal = principal
    return self

  def addAction(self, action: awacs.aws.Action):
    self._actions.append(action)
    return self

  def setEffect(self, effect: Effects):
    self._effect = effect
    return self

  def build(self) -> awacs.aws.Statement:
    if self._principal is not None:
      return awacs.aws.Statement(
          Principal = self._principal
        , Action = self._actions
        , Effect = self._effect.get()
        )
    else:
      return awacs.aws.Statement(
          Action = self._actions
        , Effect = self._effect.get()
        , Resource = self._resource
        )



class PolicyBuilder:
  def __init__(self):
    self._name: str = None
    self._statements: List[awacs.aws.Statement] = []
  
  def setName(self, name: str):
    self._name = name
    return self

  def addStatement(self, doc: awacs.aws.Statement):
    self._statements.append(doc)
    return self

  def build(self) -> Policy:
    checkForNoneValues(self)
    policyDocument = PolicyDocumentBuilder()
    for s in self._statements:
      policyDocument.addStatement(s)
    return Policy(
        PolicyName = Sub(self._name + "-${AWS::StackName}")
      , PolicyDocument = policyDocument.build()
      )



class PolicyDocumentBuilder:
  def __init__(self):
    self._statements: List[awacs.aws.Statement] = []
  
  def addStatement(self, statement: awacs.aws.Statement):
    self._statements.append(statement)
    return self
  
  def build(self) -> awacs.aws.Policy:
    return awacs.aws.Policy( Statement = self._statements )



class RoleBuilderHelper:
  def defaultAssumeRolePolicyDocument(self, service: str) -> awacs.aws.Policy:
    return PolicyDocumentBuilder() \
      .addStatement(
        StatementBuilder() \
          .setEffect(Effects.Allow) \
          .setPrincipal(awacs.aws.Principal("Service", service)) \
          .addAction(awacs.sts.AssumeRole) \
          .build()
        ) \
      .build()
    # return awacs.aws.Policy(
    #   Statement = [ awacs.aws.Statement( 
    #         Principal = awacs.aws.Principal("Service", service)
    #       , Action = [ awacs.sts.AssumeRole]
    #       , Effect = awacs.aws.Allow
    #       )
    #     ]
    #   )

  def oneClickCodePipeServicePolicy(self) -> Policy:
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
    policyDoc = awacs.aws.Policy(
        Statement = statements
      , Version = "2012-10-17"
      )
    return Policy(
        PolicyName = Sub("oneClickCodePipeServicePolicy-${AWS::StackName}")
      , PolicyDocument = policyDoc
      )


def getExample() -> str:
  t = Template()

  role = RoleBuilder() \
    .setName("ExamplePipelineRole") \
    .setAssumePolicy(RoleBuilderHelper() \
        .defaultAssumeRolePolicyDocument("codepipeline.amazonaws.com")) \
    .addPolicy(RoleBuilderHelper().oneClickCodePipeServicePolicy()) \
    .build()
  
  t.add_resource(role)
  return t.to_json()


