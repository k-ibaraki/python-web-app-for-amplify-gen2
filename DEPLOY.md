# デプロイガイド

Amplify Gen2 + GitHub Actions によるCD（継続的デプロイ）の構築手順。

## アーキテクチャ

```
┌─────────────────┐
│  GitHub Actions │
└────────┬────────┘
         │
         ├─── Backend: npx ampx pipeline-deploy
         │    └─── Docker build → ECR push → Lambda update
         │
         └─── Webhook trigger
              ↓
┌─────────────────┐
│   Amplify CD    │
└────────┬────────┘
         │
         └─── Frontend: Flet build → Amplify Hosting
              └─── ampx generate outputs → uv run build → deploy
```

## 責務の分離

| コンポーネント | 担当 | 理由 |
|--------------|------|------|
| Backend | GitHub Actions | Docker環境が必要 |
| Frontend | Amplify CD | Amplifyホスティング機能をフル活用 |

## 前提条件

- AWS CLIがインストール済み
- AWS認証情報が設定済み
- GitHubリポジトリがセットアップ済み

## 1. Amplify Gen2アプリの作成

### 1.1 Amplifyアプリを作成

```bash
aws amplify create-app --name python-web-app-for-amplify-gen2 --region ap-northeast-1
```

出力例：
```json
{
  "app": {
    "appId": "d1234567890abc",
    "name": "python-web-app-for-amplify-gen2",
    ...
  }
}
```

`appId` をメモしておく。

### 1.2 ブランチを作成

```bash
aws amplify create-branch \
  --app-id d1234567890abc \
  --branch-name main \
  --region ap-northeast-1
```

### 1.3 Auto-buildを無効化

Amplifyコンソールでホスティング設定から「Incoming webhooks」以外のトリガーを無効化します。
（GitHub pushでは直接ビルドせず、GitHub Actions経由のWebhookでトリガーするため）

## 2. Webhookの設定

### 2.1 Amplify Webhookを作成

Amplifyコンソール → アプリ → ビルドの設定 → 受信Webhook から新しいWebhookを作成します。

または、AWS CLIで作成：

```bash
aws amplify create-webhook \
  --app-id d1234567890abc \
  --branch-name main \
  --region ap-northeast-1
```

出力例：
```json
{
  "webhook": {
    "webhookArn": "arn:aws:amplify:ap-northeast-1:123456789012:apps/d1234567890abc/webhooks/abcd1234",
    "webhookId": "abcd1234",
    "webhookUrl": "https://webhooks.amplify.ap-northeast-1.amazonaws.com/prod/webhooks?id=abcd1234&token=XXXXXX&operation=startbuild",
    "branchName": "main"
  }
}
```

`webhookUrl` をメモしておく（GitHub Secretsに設定します）。

## 3. OIDC認証用のIAMロール作成

### 3.1 OIDCプロバイダーを作成

GitHubリポジトリからAWSへのOIDC認証を設定します。

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 3.2 IAMロールを作成

`trust-policy.json` を作成：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<GITHUB_USERNAME>/<REPO_NAME>:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

`<AWS_ACCOUNT_ID>`、`<GITHUB_USERNAME>`、`<REPO_NAME>` を置き換える。

IAMロールを作成：

```bash
aws iam create-role \
  --role-name GitHubActionsAmplifyDeployRole \
  --assume-role-policy-document file://trust-policy.json
```

### 3.3 必要なポリシーをアタッチ

```bash
# Amplify関連
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess-Amplify

# ECR（Dockerイメージ管理）
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

# CloudFormation（CDKデプロイ）
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess

# Lambda（関数更新）
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess

# IAM（CDKがロールを作成するため）
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/IAMFullAccess

# API Gateway
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator
```

**注意**: 上記はデモ用の権限です。本番環境では最小権限の原則に従って、必要な権限のみを付与してください。

ロールのARNをメモ：
```
arn:aws:iam::<AWS_ACCOUNT_ID>:role/GitHubActionsAmplifyDeployRole
```

## 4. GitHub Secretsの設定

GitHubリポジトリの Settings → Secrets and variables → Actions から以下を設定：

| Secret名 | 説明 | 例 |
|---------|------|-----|
| `AWS_IAM_ROLE_ARN` | OIDC認証用のIAMロールARN | `arn:aws:iam::123456789012:role/GitHubActionsAmplifyDeployRole` |
| `AMPLIFY_APP_ID` | AmplifyアプリケーションID | `d1234567890abc` |
| `AMPLIFY_WEBHOOK_URL` | Amplify受信WebhookのURL | `https://webhooks.amplify.ap-northeast-1.amazonaws.com/prod/webhooks?id=...` |

## 5. 初回デプロイ（手動）

GitHub Actionsを動かす前に、ローカルで初回デプロイを実行します。

```bash
# 依存関係インストール
npm ci

# Amplify sandboxでバックエンドをデプロイ
npx ampx sandbox --once
```

これにより、以下が生成されます：
- ECRリポジトリ
- Lambda関数
- API Gateway
- `amplify_outputs.json`

## 6. GitHub Actionsの動作確認

`main` ブランチにpushすると、自動的にデプロイが開始されます。

```bash
git add .
git commit -m "feat: setup CI/CD with GitHub Actions"
git push origin main
```

### 確認ポイント

1. **GitHub Actions** (Actions タブ)
   - "Deploy Backend to AWS Amplify Gen2" ワークフローが成功
   - バックエンドがデプロイされ、Webhookがトリガーされる

2. **Amplify Console** (AWS Console)
   - Webhookによりフロントエンドビルドが開始
   - `amplify.yml`に従ってビルド・デプロイが実行

## 7. デプロイ後の確認

### 7.1 Backend API

API GatewayのエンドポイントURLは `amplify_outputs.json` で確認できます。

```json
{
  "custom": {
    "ApiEndpoint": "https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/"
  }
}
```

または、AWS コンソール → API Gateway から確認。

### 7.2 Frontend

Amplifyコンソールまたは以下のURLでアクセス：

```
https://main.<AMPLIFY_APP_ID>.amplifyapp.com
```

## デプロイフロー

```
1. GitHub push to main
   ↓
2. GitHub Actions triggered
   ├── npm ci
   └── npx ampx pipeline-deploy
       ├── Docker build
       ├── ECR push
       ├── Lambda update
       └── API Gateway update
   ↓
3. Webhook triggers Amplify build
   ↓
4. Amplify CD starts
   ├── npm ci
   ├── npx ampx generate outputs (amplify_outputs.json)
   ├── cd frontend && uv sync
   └── uv run build
       ├── Read amplify_outputs.json
       ├── Generate config.py
       └── Build Flet web app
   ↓
5. Amplify deploys frontend/dist to Hosting
   ↓
6. Deployment complete ✅
```

## トラブルシューティング

### ECR権限エラー

```
Error: Failed to push Docker image to ECR
```

→ IAMロールに `AmazonEC2ContainerRegistryPowerUser` 権限があるか確認。

### Lambda更新エラー

```
Error: Lambda function not found
```

→ 初回デプロイ（`npx ampx sandbox --once`）が完了しているか確認。

### Amplify Webhookエラー

```
curl: (22) The requested URL returned error: 401
```

→ `AMPLIFY_WEBHOOK_URL` が正しいか確認。Amplifyコンソールで再生成も可能。

### Amplify ビルドエラー（uv not found）

```
uv: command not found
```

→ `amplify.yml`のPATH設定を確認。`$HOME/.local/bin`がPATHに含まれているか確認。

### amplify_outputs.json が見つからない

```
Error: amplify_outputs.json not found
```

→ バックエンドが正常にデプロイされているか確認。
→ `npx ampx generate outputs --branch main --app-id <APP_ID>` を手動実行して確認。

## 参考資料

- [Amplify Gen2 - Custom Pipelines](https://docs.amplify.aws/react/deploy-and-host/fullstack-branching/custom-pipelines/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
