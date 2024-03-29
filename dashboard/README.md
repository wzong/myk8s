# Kubernetes Dashboard

The goal is to expose k8s dashboard that is accessible via public internet but only by
authorized users.

Prerequisite:
* [Ingress](/network/ingress/README.md), so that the dashboard can be accessible by a host name.

## v0: built-in authentication

The [kubernetes-dashboard](https://github.com/kubernetes/dashboard) project only provides SA token
based authentications.

Pros:

* After login, what user can access is bounded to the Roles that the SA is binded to.

Cons:

* In order to login, it requires end user to provide an SA-token or upload the kube_config
  file. There is no OAuth authentication or SSO which are much more popular/convinient
  authentication mechanism.
* I tend to have security concerns about such "Forever Tokens" stored in my computer and browser
  cookies.

This can be easily achieved following the docs on Github.

## v1: SSO + optional SkipLogin

### v1.1: SSO with OAuth2 Proxy

It seems to be popular to place the k8s dashboard web UI behind an
[oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy).

Pros:

* Extra protection for the k8s dashboard web UI (e.g. against brute force attacks).
* The OAuth2 Proxy can serve as an SSO gateway, which is shared with many other services in the
  cluster.

Cons:

* After OAuth2 authentication, the web UI will still require an SA-token to authenticate.
  So the inconvinience is still there, though security risk maybe a little bit less with OAuth2.

This can be achieved with:

1. Follow the oauth2-proxy docs and bring up an instance.
2. Create an Ingress for the `kubernetes-dashboard` Service, with
   `nginx.ingress.kubernetes.io/auth-url` annotation point to the oauth2-proxy endpoints.

See the [auth module](../auth/README.md) for the deployment steps. After that, the dashboard can be
visited at `https://dashboard.mysite.com` and redirect to `https://login.mysite.com/oauth2/start`
for login (Please ensure that the dashboard and oauth2 hosts are
[SameSite](https://web.dev/samesite-cookies-explained/) for security compliance).

### v1.2: SkipLogin

To bypass the SA-token authenticate after OAuth2 authentication, we can enable the SkipLogin
feature on the K8S dashboard server. The dashboard server can display a `SKIP` button in the login page. Clicking on the button will bypass the login, and use previledges of the dashboard server's SA, which by default has near-zero access to the cluster's information.
Therefore we also need to expand the previledges of the dashboard server SA.

Pros:

* Eliminated the SA-token based authentication step.

Cons:

* It's not recommended to let dashboard SA to have wide range of previledges, which is less secure.
* Anyone who can pass the OAuth2 authentication will have the same access. It's impossible to
  achieve more granular access control.

This can be achieved with:

1. Grant the dashboard server SA `cluster-admin` role:

    ```shell
    kubectl apply -f v1/dashboard_admin.yaml
    ```

2. Deploy dashboard server:

    ```shell
    kubectl apply -f v1/dashboard.yaml
    ```

    The [v1/dashboard.yaml](v1/dashboard.yaml) which is a copy of the recommended configs from
    [kubernetes-dashboard](https://github.com/kubernetes/dashboard), but enabled the following
    flags to allow SKIP LOGIN.

    ```shell
    --enable-skip-login
    --disable-settings-authorizer
    ```

3. A `SKIP` button will be displayed in the dashboard login UI to bypass.

## (TODO) v2: SSO with Auto-SA-Auth

At the low-level, the SA-token based authentication flow is as below:

1. After user enters the SA token and login, a request with the following header will be sent
   to the server:
    ```
    Authorization: Bearer <token>
    ```

2. Server will respond with `Set-Cookie` headers with the token which will be carried with all
   subsequent request to authenticate.

Therefore, ideally, the following can help us achieve secure SSO without manual SA-Auth:

1. Adopt another reverse proxy server in between the `oauth2-proxy` and `kubernetes-dashboard`.
2. Based on the authenticated user (via OAuth2), the auth endpoint/proxy can look up the SA-tokens
   that the user should have access to.
3. Proxy server attach `Authorization` header to the upstream with the SA-token.
4. Response may contain SA-token that we don't want to expose to the end user, and we need to
   strip those headers/cookies.

The proposal is highly customized to fit the current
[k8s dashboard auth flow](https://github.com/kubernetes/dashboard/tree/master/docs/user/access-control). I'm not sure if it's subject to change or if the project has any plan to natively
support OAuth2 as an alternative to SA-token. It seems a little bit overkill for me for now.
