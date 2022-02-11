# pipeline/pipeline_stack.py

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_codebuild as codebuild,
                     aws_codecommit as codecommit,
                     aws_codepipeline as codepipeline,
                     aws_codepipeline_actions as codepipeline_actions)


class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        artifacts_bucket = s3.Bucket(self, "ArtifactsBucket")
        
   ###source stage
     # Import existing CodeCommit sam-app repository
        code_repo = codecommit.Repository.from_repository_name(self, "AppRepository", "sam-app")
        
        # Pipeline creation starts
        pipeline = codepipeline.Pipeline(self, "Pipeline",
          artifact_bucket = artifacts_bucket
        )
        
        # Declare source code as an artifact
        source_output = codepipeline.Artifact()
        
        # Add source stage to pipeline
        pipeline.add_stage(
            stage_name = "Source", 
            actions = [ 
                codepipeline_actions.CodeCommitSourceAction(
                    action_name = "Source",
                    branch = "main",
                    output = source_output,
                    repository = code_repo,
                )
            ]
        )


###add build stage
        # Declare build output as artifacts
        build_output = codepipeline.Artifact()
        
        # Declare a new CodeBuild project
        build_project = codebuild.PipelineProject(self, "Build", 
            environment = codebuild.BuildEnvironment(
                build_image = codebuild.LinuxBuildImage.STANDARD_5_0,
            ),
            environment_variables = {
                'PACKAGE_BUCKET': codebuild.BuildEnvironmentVariable(value = artifacts_bucket.bucket_name),
            },
        )
        
        # Add the build stage to our pipeline
        pipeline.add_stage(
            stage_name = "Build", 
            actions = [
                codepipeline_actions.CodeBuildAction(
                    action_name = "Build",
                    project = build_project,
                    input = source_output,
                    outputs = [build_output],
                )
            ]
        )