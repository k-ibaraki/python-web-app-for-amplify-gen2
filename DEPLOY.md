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
6. サービスロールは、新規作成でOK
7. 「保存してデプロイ」をクリック

**注意**: 初回デプロイは失敗する可能性がありますが問題ありません（バックエンドがまだデプロイされていないため）。

### 1.2 アプリIDを確認

作成されたアプリのURLから、アプリIDを確認します。

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

### 3.1 OIDCプロバイダーを作成(GitHub Actions用)

既に作成済みの場合はスキップしてください。

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

※ 既に存在する場合はエラーになります。

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
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:<GITHUB_USERNAME>/<REPO_NAME>:ref:refs/heads/main",
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

# API Gateway
aws iam attach-role-policy \
  --role-name GitHubActionsAmplifyDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator
```

**注意**: 本番環境では最小権限の原則に従って、必要な権限のみを付与してください。

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

## 5. GitHub Actionsの動作確認

`main` ブランチにpushすると、自動的にデプロイが開始されます。
または、手動でワークフローをトリガーすることもできます。

```bash
git add .
git commit -m "feat: setup CI/CD with GitHub Actions"
git push origin main
```

### 確認ポイント

#### 5.1 GitHub Actions（バックエンド）

1. GitHubリポジトリの「Actions」タブを開く
2. "Deploy Backend to AWS Amplify Gen2" ワークフローが実行中
3. 以下のステップが成功することを確認：
   - Configure AWS credentials
   - Deploy backend with Amplify pipeline
   - Trigger Amplify frontend build

#### 5.2 Amplify Console（フロントエンド）

1. [AWS Amplify Console](https://console.aws.amazon.com/amplify/)を開く
2. アプリを選択
3. Webhookによりビルドが開始されることを確認
4. ビルドログで以下を確認：
   - `npx ampx generate outputs` が成功
   - `uv run build` が成功
   - デプロイ完了

## 6. デプロイ後の確認

### 6.1 Backend API

API GatewayのエンドポイントURLは `amplify_outputs.json` で確認できます。

```bash
cat amplify_outputs.json | jq '.custom.ApiEndpoint'
```

または、AWS Console → API Gateway → APIs から確認。

### 6.2 Frontend

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

## 参考資料

- [Amplify Gen2 - Custom Pipelines](https://docs.amplify.aws/react/deploy-and-host/fullstack-branching/custom-pipelines/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
