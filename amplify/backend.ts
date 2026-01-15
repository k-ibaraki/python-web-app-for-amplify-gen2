import { defineBackend } from "@aws-amplify/backend";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { Duration } from "aws-cdk-lib";
import { Platform } from "aws-cdk-lib/aws-ecr-assets";
import { ApiGatewayToLambda } from "@aws-solutions-constructs/aws-apigateway-lambda";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const backend = defineBackend({});

const apiStack = backend.createStack("ApiStack");

// FastAPI backend as Docker Lambda (x86_64 for GitHub Actions compatibility)
const apiFunction = new lambda.DockerImageFunction(apiStack, "ApiFunction", {
  code: lambda.DockerImageCode.fromImageAsset(join(__dirname, "api"), {
    platform: Platform.LINUX_AMD64,
  }),
  memorySize: 512,
  timeout: Duration.seconds(30),
  architecture: lambda.Architecture.X86_64,
  environment: {
    API_ROOT_PATH: "/prod",
  },
});

// API Gateway + Lambda integration
const apiGateway = new ApiGatewayToLambda(apiStack, "ApiGatewayToLambda", {
  existingLambdaObj: apiFunction,
  apiGatewayProps: {
    proxy: true,
    defaultMethodOptions: {
      authorizationType: apigateway.AuthorizationType.NONE,
    },
    defaultCorsPreflightOptions: {
      allowOrigins: ["*"],
      allowMethods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
      allowHeaders: ["*"],
    },
  },
});

// Output the API Gateway URL
backend.addOutput({
  custom: {
    ApiEndpoint: apiGateway.apiGateway.url,
  },
});
