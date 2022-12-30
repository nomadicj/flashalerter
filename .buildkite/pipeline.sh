#!/usr/bin/env bash
set -eo pipefail

function generate_lint() {
  cat <<STEP

  - label: ":pencil: Lint"
    command: make lint
    
STEP
}

function generate_test() {
  cat <<STEP

  - label: ":hash: Unit Tests"
    command: make test

STEP
}

function generate_build() {
  cat <<STEP

  - label: ":building_construction: Build"
    command: make deploy

STEP
}

function generate_wait() {
  cat <<STEP

  - wait

STEP
}

function generate_block() {
  cat <<STEP

  - block: "Approval required to; ${1}? :thumbsup:"

STEP
}

function generate_push() {
  cat <<STEP

  - label: ":city_sunrise: Push"
    command: make push

STEP
}

function generate_deploy() {
  cat <<STEP

  - label: ":city_sunrise: Deploy"
    command: make deploy

STEP
}

function generate_pipeline() {
  # create header of pipeline
#  cat << EOF
#env:
#  
#EOF
  echo "steps:"

  # Lint the root of the repo
  # generate_lint
  # generate_test
  generate_build
  generate_wait
  generate_push
  # generate_deploy
}

# upload dynamically generated pipeline to buildkite
generate_pipeline #| buildkite-agent pipeline upload