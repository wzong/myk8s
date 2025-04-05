# Corp SSO

## Goals

* Protect Ingress resources under `.corp.mysite.com` with authentication, so that only "specific"
  logged-in users can have access.
* Provides Single-Sign-On so that one login will bypass login for all Ingress hosts.

## Overview

The Kubernetes Ingress Nginx has provided solution in
[doc](https://kubernetes.github.io/ingress-nginx/examples/auth/oauth-external-auth/) about
authentication, which uses [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) to provide
an auth endpoint for the Ingress Nginx server.

The login flow works as below:

1. Each `$host` (e.g. `app1.corp.mysite.com`) will be configured `auth-url` and `auth-signin` to
   check / redirect users to signin.

2. Once a request is made to the `$host/$request_uri`, the Ingress Nginx will check with
   `login.corp.mysite.com/oauth2/auth` to see if request is authenticated.

3. If not Nginx Ingress will send 302 to redirect to
   `login.corp.mysite.com/oauth2/start?rd=$scheme://$host$request_uri$args`.

4. OAuth2 server will send 302 to redirect to the external oauth2 provider for login
   (e.g. `https://login.github.com?redirect_url=https://login.corp.mysite.com/oauth2/callback&state=<token>$host/$request_uri`)

5. After user successful login, the external oauth2 provider redirect back to OAuth2 proxy base on
   the `?redirect_url` param with login tokens:
   (e.g. `https://$host/oauth2/callback?token=...&state=<token>$host/$request_uri...`)

6. OAuth2 server will validate the token with the oauth2 provider and respone with `Set-Cookie`
   header (from the `token` url param) to authenticate the client. The response will be a 302
   redirect to `$host$request_uri$args` (from the `state` url param).

## Customize oauth2-proxy

The above flow is slightly different from the conventional setup for oauth2-proxy server. Below
are the reasons and corresponding flags (args) I need to customize:

* In step5, most external oauth2 provider requires allowlisting the value of `?redirect_url=`,
  otherwise they will reject with 403 response. However, conventional setup exposes oauth2-proxy
  server as an endpoint of each individual `$host` (e.g. `app1.corp.mysite.com/` proxy_pass to the
  actual Service, and `app1.corp.mysite.com/oauth2/` proxy_pass to the oauth2-proxy server). With
  that I need to allowlist each individual endpoint in the OAuth2 provider's client key, which is
  not scalable. Therefore I'm using a single callback host `login.corp.mysite.com/oauth2/callback`
  for the oauth2-proxy server. And upon `callback`, let oauth2-proxy server redirect to the
  destination host (e.g. `app1.corp.mysite.com`)

* In step6, the auth cookie in `Set-Cookie` will only set for the redirect url
  `login.corp.mysite.com`, so after the it further redirects to the destination host (e.g.
  `app1.corp.mysite.com`) the cookie is not set and it will infitely loop back to start of the
  workflow. To solve that, I need to set the `--cookie-domain=corp.mysite.com` flag on the
  oauth2-proxy server, so that the final `Set-Cookie` will contain something like `Domain=corp.mysite.com` and the auth cookie will work for all sub-domains under `corp.mysite.com`.

* In step4, the value of `$scheme://$host$request_uri$args` (e.g. `https://app1.corp.mysite.com`)
  must be set in `--whitelist-domain` flag, otherwise the value will be missing in the `state` url
  param and after `callback` to `login.corp.mysite.com`, it won't redirect to actual app.
  The flag allows wildcard. So I need to set something like `--whitelist-domain=.corp.mysite.com`.

* In step5, I want to restrict which logged in user can access the host (e.g. users belongs to
  a specific Github organization + Team). So I need to configure additional oauth-provider specific
  server flags.

With the updated login flow, SSO can be achieved.

## Usage

1. Create OAuth2 Provider secrets and deploy oauth2-proxy server:

    Note: The `cookie-domain` config should be the corp SSO domain (e.g. `.corp.mysite.com`).

    * GitHub:

      ```shell
      kubectl create namespace oauth2-proxy

      kubectl create secret generic oauth2-github-secret -n oauth2-proxy \
      --from-literal=cookie_secret=$(python -c 'import os,base64; print(base64.b64encode(os.urandom(16)).decode("ascii"))') \
      --from-literal=client_id=<your github oauth app client id> \
      --from-literal=client_secret=<your github oauth app client secret> \
      --from-literal=github_org=<your github org> \
      --from-literal=github_team=<your github team> \
      --from-literal=cookie_domain=.corp.mysite.com \
      --from-literal=whitelist_domains=.corp.mysite.com


      kubectl apply -f github.yaml
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

      kubectl apply -f azure_ad.yaml
      ```

2. Deploy Ingress for the oauth2 endpoints at `login.corp.mysite.com`:

    ```shell
    export DOMAIN=mysite.com && \
    cat ingress_login.template.yaml | envsubst '${DOMAIN}' | kubectl apply -f -
    ```

3. Deploy Ingress for each corpsso app

    Taking the `hello` service as an example:

    ```shell
    export NAME=hello && \
    export DOMAIN=mysite.com && \
    export BACKEND_SERVICE_NAME=hello-ingress && \
    export BACKEND_SERVICE_NAMESPACE=examples && \
    cat ingress_app.template.yaml | \
    envsubst '${NAME},${DOMAIN},${BACKEND_SERVICE_NAME},${BACKEND_SERVICE_NAMESPACE}' | \
    kubectl apply -f - &&
    echo "Host: ${NAME}.corp.${DOMAIN}"
    ```
