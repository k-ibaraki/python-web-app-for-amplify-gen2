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

- AWSアカウント
- GitHubリポジトリ
- リポジトリがGitHubにpush済み

## 1. Amplify Gen2アプリの作成（GitHub連携）

### 1.1 Amplifyコンソールでアプリを作成

1. [AWS Amplify Console](https://console.aws.amazon.com/amplify/)を開く
2. 「新しいアプリ」→「ホスティング」→「既存のコードをデプロイ」
3. GitHubを選択して認証
4. リポジトリとブランチ（`main`）を選択
5. ビルド設定で「既存の設定を検出」を選択（`amplify.yml`が自動検出される）
6. **重要**: 「詳細設定」で以下を設定：
   - サービスロール: 新規作成または既存のロールを選択
   - 環境変数: 不要（後で設定）
7. 「保存してデプロイ」をクリック

**注意**: 初回デプロイは失敗する可能性がありますが問題ありません（バックエンドがまだデプロイされていないため）。

### 1.2 アプリIDを確認

作成されたアプリのURLから、アプリIDを確認します：

```
https://console.aws.amazon.com/amplify/home?region=ap-northeast-1#/d1234567890abc
                                                                    ^^^^^^^^^^^^^^
                                                                    これがApp ID
```

または、「アプリの設定」→「全般」で確認できます。

### 1.3 自動ビルドを無効化

1. アプリのページで「ビルドの設定」→「ブランチ」
2. `main` ブランチの設定を開く
3. 「自動ビルド」を**オフ**に設定
   - GitHub pushでは自動ビルドしない
   - Webhookのみでビルドをトリガーする

## 2. Webhookの設定

### 2.1 Amplify Webhookを作成

1. アプリのページで「ビルドの設定」→「受信Webhook」
2. 「Webhookを作成」をクリック
3. 以下を入力：
   - 名前: `github-actions-trigger`（任意）
   - ブランチ: `main`
4. 「Webhookを作成」をクリック
5. 生成されたWebhook URLをコピー（後でGitHub Secretsに設定）

Webhook URLの例：
```
https://webhooks.amplify.ap-northeast-1.amazonaws.com/prod/webhooks?id=abcd1234&token=XXXXXX&operation=startbuild
```

**重要**: このURLには認証トークンが含まれるため、安全に管理してください。

## 3. OIDC認証用のIAMロール作成

### 3.1 OIDCプロバイダーを作成

既に作成済みの場合はスキップしてください。

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

既に存在する場合はエラーが出ますが、無視してOKです。

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

以下を置き換えてください：
- `<AWS_ACCOUNT_ID>`: AWSアカウントID（12桁）
- `<GITHUB_USERNAME>`: GitHubユーザー名またはOrg名
- `<REPO_NAME>`: リポジトリ名

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

ロールのARNを確認：
```bash
aws iam get-role --role-name GitHubActionsAmplifyDeployRole --query 'Role.Arn' --output text
```

出力例：
```
arn:aws:iam::123456789012:role/GitHubActionsAmplifyDeployRole
```

## 4. GitHub Secretsの設定

GitHubリポジトリの Settings → Secrets and variables → Actions → Repository secrets から以下を設定：

| Secret名 | 説明 | 取得方法 |
|---------|------|---------|
| `AWS_IAM_ROLE_ARN` | OIDC認証用のIAMロールARN | 手順3.3で確認 |
| `AMPLIFY_APP_ID` | AmplifyアプリケーションID | 手順1.2で確認 |
| `AMPLIFY_WEBHOOK_URL` | Amplify受信WebhookのURL | 手順2.1で作成 |

## 5. 初回デプロイ（ローカルから）

GitHub Actionsを動かす前に、ローカルでバックエンドを初回デプロイします。

```bash
# 依存関係インストール
npm ci

# Amplify sandboxでバックエンドをデプロイ
npx ampx sandbox --once
```

実行すると、以下が作成されます：
- ECRリポジトリ
- Lambda関数
- API Gateway
- `amplify_outputs.json`

完了後、`amplify_outputs.json`が生成されていることを確認：

```bash
cat amplify_outputs.json
```

## 6. GitHub Actionsの動作確認

`main` ブランチにpushすると、自動的にデプロイが開始されます。

```bash
git add .
git commit -m "feat: setup CI/CD with GitHub Actions"
git push origin main
```

### 確認ポイント

#### 6.1 GitHub Actions（バックエンド）

1. GitHubリポジトリの「Actions」タブを開く
2. "Deploy Backend to AWS Amplify Gen2" ワークフローが実行中
3. 以下のステップが成功することを確認：
   - Configure AWS credentials
   - Deploy backend with Amplify pipeline
   - Trigger Amplify frontend build

#### 6.2 Amplify Console（フロントエンド）

1. [AWS Amplify Console](https://console.aws.amazon.com/amplify/)を開く
2. アプリを選択
3. Webhookによりビルドが開始されることを確認
4. ビルドログで以下を確認：
   - `npx ampx generate outputs` が成功
   - `uv run build` が成功
   - デプロイ完了

## 7. デプロイ後の確認

### 7.1 Backend API

API GatewayのエンドポイントURLは `amplify_outputs.json` で確認できます。

```bash
cat amplify_outputs.json | jq '.custom.ApiEndpoint'
```

または、AWS Console → API Gateway → APIs から確認。

### 7.2 Frontend

Amplifyコンソールに表示されるURLでアクセス：

```
https://main.<AMPLIFY_APP_ID>.amplifyapp.com
```

アプリのページで「アプリURLを表示」をクリックして確認できます。

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
3. curl Webhook (trigger Amplify build)
   ↓
4. Amplify CD starts
   ├── npm ci
   ├── npx ampx generate outputs (amplify_outputs.json)
   ├── cd frontend
   ├── uv sync
   └── uv run build
       ├── Read amplify_outputs.json
       ├── Generate config.py with API URL
       └── Build Flet web app
   ↓
5. Amplify deploys frontend/dist to Hosting
   ↓
6. Deployment complete ✅
```

## トラブルシューティング

### GitHub Actions: OIDC認証エラー

```
Error: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**原因**: IAMロールの信頼ポリシーが正しくない

**解決策**:
1. `trust-policy.json`の`<GITHUB_USERNAME>`、`<REPO_NAME>`が正しいか確認
2. IAMコンソールでロールの信頼関係を確認

### GitHub Actions: ECR権限エラー

```
Error: Failed to push Docker image to ECR
```

**解決策**: IAMロールに `AmazonEC2ContainerRegistryPowerUser` 権限があるか確認

### GitHub Actions: Lambda更新エラー

```
Error: Lambda function not found
```

**解決策**: 初回デプロイ（`npx ampx sandbox --once`）が完了しているか確認

### Amplify: Webhookエラー

```
curl: (22) The requested URL returned error: 401
```

**解決策**: `AMPLIFY_WEBHOOK_URL` が正しいか確認。Amplifyコンソールで再生成も可能。

### Amplify: uv not found

```
uv: command not found
```

**解決策**: `amplify.yml`のPATH設定を確認。ビルドログで`uv --version`が成功しているか確認。

### Amplify: amplify_outputs.json が見つからない

```
Error: amplify_outputs.json not found
```

**解決策**:
1. バックエンドが正常にデプロイされているか確認
2. Amplifyコンソールで`npx ampx generate outputs`のログを確認
3. App IDが正しいか確認

### Amplify: Flet buildエラー

```
Error: No module named 'flet'
```

**解決策**: `uv sync`が成功しているか確認。ビルドログで依存関係のインストールを確認。

## セキュリティのベストプラクティス

### 本番環境向けのIAM権限最適化

デモ用のフル権限ポリシーの代わりに、最小権限のカスタムポリシーを作成してください。

例：`amplify-deploy-policy.json`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "amplify:*"
      ],
      "Resource": "arn:aws:amplify:ap-northeast-1:*:apps/<AMPLIFY_APP_ID>/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration"
      ],
      "Resource": "arn:aws:lambda:ap-northeast-1:*:function:amplify-*"
    }
  ]
}
```

## 参考資料

- [Amplify Gen2 - Custom Pipelines](https://docs.amplify.aws/react/deploy-and-host/fullstack-branching/custom-pipelines/)
- [Amplify Gen2 - Webhooks](https://docs.aws.amazon.com/amplify/latest/userguide/webhooks.html)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
