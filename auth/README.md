# Authentication

## Goals

* Protect Ingress resources with authentication so that only specific logged-in users can have
  access.
* Provides Single-Sign-On so that one login will bypass login for all Ingress hosts.

## Overview

The Kubernetes Ingress Nginx has provided solution in
[doc](https://kubernetes.github.io/ingress-nginx/examples/auth/oauth-external-auth/) about
authentication, which uses [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) to provide
an auth endpoint for the Ingress Nginx server.

The login flow works as below:

1. Each host to project comes with 2 Ingress resource: `$host/` for the actual service backend,
   and `$host/oauth2/` to point to the oauth2 proxy server.
2. Once a request is made to the `$host/$request_uri`, the Ingress Nginx will check with
   `$host/oauth2/auth` to see if request is authenticated.
3. If not Nginx Ingress will send 302 to redirect to `$host/oauth2/start?rd=$host/$request_uri`.
4. OAuth2 server will send 302 to redirect to the external oauth2 provider for login
   (e.g. `https://login.github.com?redirect_url=https://$host/oauth2/callback?rd=$host/$request_uri`)
5. After user successful login, the external oauth2 provider redirect back to OAuth2 proxy base on
   the `?redirect_url` param with login tokens:
   (e.g. `https://$host/oauth2/callback?&rd=$host/$request_uri&token=...`)
6. OAuth2 server will validate the token with the oauth2 provider and respone with `Set-Cookie`
   header to authenticate the client.

However, this login flow works only for a single Ingress host. And we need to solve the 2 problems
below, which will make some minor change to the default login flow:

* The auth cookie in `Set-Cookie` of step6 above will only work for a single host. To solve that,
  we can set the `--cookie-domain` flag on the oauth2-proxy server, so that the final `Set-Cookie`
  will contain something like `Domain=mysite.com` and the auth cookie will work for all sub-domains
  of `mysite.com`.
* In step5, most external oauth2 provider would restrict what `?redirect_url=` can be, otherwise
  they will reject with 403 response. To solve that, we need to make oauth2-proxy server to have
  a static subdomain (e.g. `login.mysite.com/oauth2`) instead of exposed as endpoints of individual
  `$host` (e.g. `app1.mysite.com/oauth2/`, `app2.mysite.com/oauth2/`, ...).
  * Another subproblem I found is that, oauth2-proxy by default restricts that the `?rd=...`
    must be the same host (e.g. `login.mysite.com`, but not `app1.mysite.com`). Otherwise in step4,
    it will wipe out the `rd` part in the `?redirect_url`. To solve that, we need to set the
    `--whitelist-domain=.mysite.com` to allowlist all subdomains.

With the updated login flow, SSO can be achieved.

## Deploy OAuth2-Proxy

1. Create OAuth2 Provider secrets and deploy oauth2-proxy server:

    Note: The `cookie-domain` config should be the SSO domain (e.g. `.mysite.com`), such that all
    subdomains (e.g. `login.mysite.com`, `myapp1.mysite.com`, ...) have access to.

    * GitHub:

      ```shell
      kubectl create namespace oauth2-proxy

      kubectl create secret generic oauth2-github-secret -n oauth2-proxy \
      --from-literal=cookie_secret=$(python -c 'import os,base64; print(base64.b64encode(os.urandom(16)).decode("ascii"))') \
      --from-literal=client_id=<your github oauth app client id> \
      --from-literal=client_secret=<your github oauth app client secret> \
      --from-literal=github_org=<your github org> \
      --from-literal=github_team=<your github team> \
      --from-literal=cookie_domain=<your SSO domain>

      kubectl apply -f v1/proxy_github.yaml
      ```

      Note: The access token of github never expires unless end user explicitly revoke the OAuth
      token. There seem to be beta
      [features](https://docs.github.com/en/developers/apps/building-github-apps/refreshing-user-to-server-access-tokens)
      to enforce token expiration.

    * AzureAD: (This was just to play around AzureAD, but it proved to be way too complex than what
      I need, so I'm switching back to Github)

      ```shell
      kubectl create namespace oauth2-proxy

      kubectl create secret generic azure-ad-secret -n oauth2-proxy \
      --from-literal=cookie_secret=$(python -c 'import os,base64; print(base64.b64encode(os.urandom(16)).decode("ascii"))') \
      --from-literal=oidc_issuer_url=https://login.microsoftonline.com/<your AD tenant id> \
      --from-literal=client_id=<your azure AD client id> \
      --from-literal=client_secret=<your azure AD client secret> \
      —-from-literal=cookie_domain=mysite.com

      kubectl apply -f v1/proxy_azure_ad.yaml
      ```

2. Deploy Ingress for the oauth2 endpoints:

    ```shell
    export OAUTH2_HOST=login.mysite.com && \
    cat ingress_oauth2.template.yaml | envsubst | kubectl apply -f -
    ```

    ```shell
    export OAUTH2_HOST=login.mysite.com && \
    export INGRESS_HOST=dashboard.mysite.com && \
    export BACKEND_SERVICE_NAME=kubernetes-dashboard && \
    export BACKEND_SERVICE_NAMESPACE=kubernetes-dashboard && \
    cat ingress.template.yaml | envsubst | kubectl apply -f -
    ```

3. Then service can be accessible at `https://<YOUR_HOSTNAME>` and will be redirected to
   relevant `https://<YOUR_HOSTNAME>/oauth2/` endpoints for authentication.

## Deploy Ingress for each app

Taking the `kubernetes-dashboard` service as an example:

```shell
export INGRESS_HOST=dashboard.mysite.com && \
export OAUTH2_HOST=login.mysite.com && \
export BACKEND_SERVICE_NAME=kubernetes-dashboard && \
export BACKEND_SERVICE_NAMESPACE=kubernetes-dashboard && \
cat ingress_app.template.yaml | \
envsubst '${INGRESS_HOST},${OAUTH2_HOST},${BACKEND_SERVICE_NAME},${BACKEND_SERVICE_NAMESPACE}' | \
kubectl apply -f -
```

In my case, all Ingress resources will be created under the `oauth2-proxy` namespace
(instead of namespace of the app). This is to make it easier for me to manage all subdomains in one place, and also helps avoid conflicts (since hostnames are "global" resources).

```shell
kubectl get ing -n oauth2-proxy
```
