#!/usr/bin/env bash
set -eo pipefail

# The Buildkite pipeline loads this file from the master branch only!
# Editing this in a branch will not result in the pipeline changing!

# separate account lists
management_accounts=$(find org/management -maxdepth 1 -mindepth 1 -type d | grep -vE "templates|networking")
shared_accounts=$(find org/shared -maxdepth 2 -mindepth 2 -type d)
spoke_dev=$(find org/spoke/stub -maxdepth 1 -mindepth 1 -type d | grep dev)
spoke_test=$(find org/spoke/stub -maxdepth 1 -mindepth 1 -type d | grep test)
spokes=$(find org/spoke -maxdepth 2 -mindepth 2 -type d | grep -v 'templates' | grep -v stub)

function generate_lint() {
  cat <<STEP
  - label: ":pencil: Lint"
    command: make lint
STEP
}

function generate_test() {
  local deploy_list=${1}

  # generate parallel test for all terraform configurations
  echo "${deploy_list}" | while read -r account; do
    cat <<STEP
  - label: ":hash: TFSEC Test"
    command: make test
    env:
      ACCOUNT_PATH: ${account}
STEP
  done
}

function generate_build() {
  local deploy_list=${1}
  local branch_filter=${2}

  echo "${deploy_list}" | while read -r account; do
    cat <<STEP
  - label: ":building_construction: Build: ${account/org\///}"
    command: |
      make build
      if [[ -f "${account}/tf_plan_changes" ]]; then
        echo -e "Changes planned for ${account/org\///}\n\n" > "${account}/annotation"
        echo '<pre class="term"><code>' >> "${account}/annotation"
        cat ${account}/tf_plan_changes | terminal-to-html >> "${account}/annotation"
        echo '</code></pre>' >> "${account}/annotation"

        cat "${account}/annotation" | buildkite-agent annotate --style "warning" --context "${account/org\///}" || \
        echo -e "${account}\n\nFAILED TO PRINT ANNOTATION - PLEASE CHECK THE BUILD OUTPUT FOR IT" buildkite-agent annotate --style "warning" --context "${account/org\///}"
      fi
      ls ${account}/terraform.plan > /dev/null # check the plan file was created, sometimes TF crashes don't error, so this is how we can check for that
    artifact_paths:
      - "${account}/terraform.plan"
      - "${account}/tf_plan_changes"
    branches: "${branch_filter}"
    concurrency: 1
    concurrency_group: ${BUILDKITE_PIPELINE_SLUG}/${account}
    env:
      ACCOUNT_PATH: ${account}

STEP
  done
}

function generate_deploy() {
  local deploy_list=${1}
  local branch_filter=${2}

  echo "${deploy_list}" | while read -r account; do
    if [[ "${account}" == *"spoke"* ]] || [[ "${account}" == *"shared"* ]]; then
      TF_PATH=org/_account_template
    else
      TF_PATH="${account}"
    fi

    cat <<STEP
  - label: ":city_sunrise: Deploy: ${account/org\///}"
    command: |
      buildkite-agent artifact download "${account}/terraform.plan" . || true
      if [[ -f "${account}/tf_plan_changes" ]]; then
        echo "There were changes in the plan, triggering secops"
        ACCOUNT_ID="\$(cat ${account}/_account_id)" bash .buildkite/trigger_secops_pipeline.sh
      else
        echo "There were no changes in the plan (couldnt find ${account}/terraform.plan) so skipping the terraform apply"
      fi
      make deploy
    branches: "${branch_filter}"
    concurrency: 1
    concurrency_group: ${BUILDKITE_PIPELINE_SLUG}/${account}
    env:
      ACCOUNT_PATH: ${account}

STEP
  done
}

function generate_wait() {
  cat <<STEP

  - wait

STEP
}

function generate_block() {
  # Provide one quoted parameter - the prompt to display on the block button
  # e.g. generate_block "Deploy to Accounts"
  cat <<STEP

  - block: "Approval required to; ${1}? :thumbsup:"
    branches: master

STEP
}

function generate_pipeline() {
  # create header of pipeline
  cat << EOF
env:
  HTTPS_PROXY: "http://proxy.nbs-management-networking.aws.nbscloud.co.uk:3128"
  HTTP_PROXY: "http://proxy.nbs-management-networking.aws.nbscloud.co.uk:3128"
  https_proxy: "http://proxy.nbs-management-networking.aws.nbscloud.co.uk:3128"
  http_proxy: "http://proxy.nbs-management-networking.aws.nbscloud.co.uk:3128"
  BUILDKITE_ARTIFACT_UPLOAD_DESTINATION: "s3://nbs-management-master-terraform-artifacts/buildkite/${BUILDKITE_BUILD_NUMBER}#${BUILDKITE_JOB_ID}"
  BUILDKITE_S3_DEFAULT_REGION: "eu-west-2"
  BUILDKITE_S3_ACL: "private"
  no_proxy: "169.254.169.254,localhost,.aws.nbscloud.co.uk"
  NO_PROXY: "169.254.169.254,localhost,.aws.nbscloud.co.uk"
EOF
  echo "steps:"

  # Lint the root of the repo
  generate_lint
  generate_test "modules"
  generate_wait
  # Always build networking first
  generate_build "org/management/networking"
  generate_block "deploy to Networking"
  generate_deploy "org/management/networking" "master"
  generate_wait
  # Build and deploy stub-dev in pr's
  generate_build "${spoke_dev}" "!master"
  generate_wait
  generate_deploy "${spoke_dev}" "!master"
  # build remaining accounts, stub-test in master only
  generate_build "${management_accounts}" ""
  generate_build "${shared_accounts}" ""
  generate_build "${spoke_test}" "master"
  generate_build "${spokes}" ""
  # Require approval before deploying, deploy to stub-test first
  generate_block "deploy to Accounts"
  generate_deploy "${spoke_test}" "master"
  generate_wait
  # Deploy to landing-zone accounts
  generate_deploy "${management_accounts}" "master"
  generate_deploy "${shared_accounts}" "master"
  # Deploy to customer accounts
  generate_block "deploy to Spokes"
  generate_deploy "${spokes}" "master"
}

# upload dynamically generated pipeline to buildkite
generate_pipeline | buildkite-agent pipeline upload
