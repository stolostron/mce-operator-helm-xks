# mce-operator-helm-xks

An alternative installation method for the backplane-operator using helm charts on non-OpenShift Kubernetes platforms.

_Red Hat does not provide commercial support for the content of this repo.
Any assistance is purely on a best-effort basis, as resources permit._

```
#############################################################################
DISCLAIMER: THE CONTENT OF THIS REPO IS EXPERIMENTAL AND PROVIDED **"AS-IS"**

THE CONTENT IS PROVIDED AS REFERENCE WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#############################################################################
```

## Prerequisites

- cert-manager
- kube-prometheus
- metal3

## Installation

helm install multicluster-engine charts/multicluster-engine -n multicluster-engine

## License

Copyright 2025.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
