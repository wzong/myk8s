load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "new_git_repository")

# --------------------------------------------------------------------------------------------------
# rules_cc contains a Starlark implementation of C++ rules in Bazel
# --------------------------------------------------------------------------------------------------
http_archive(
    name = "rules_cc",
    urls = ["https://github.com/bazelbuild/rules_cc/releases/download/0.0.10-rc1/rules_cc-0.0.10-rc1.tar.gz"],
    sha256 = "d75a040c32954da0d308d3f2ea2ba735490f49b3a7aa3e4b40259ca4b814f825",
)

# --------------------------------------------------------------------------------------------------
# bazel_skylib contains common useful functions and rules for Bazel
# --------------------------------------------------------------------------------------------------
http_archive(
    name = "bazel_skylib",
    sha256 = "bc283cdfcd526a52c3201279cda4bc298652efa898b10b4db0837dc51652756f",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/bazel-skylib/releases/download/1.7.1/bazel-skylib-1.7.1.tar.gz",
        "https://github.com/bazelbuild/bazel-skylib/releases/download/1.7.1/bazel-skylib-1.7.1.tar.gz",
    ],
)

load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")

bazel_skylib_workspace()

# --------------------------------------------------------------------------------------------------
# rules_python defines rules for generating Python code from Protocol Buffers
# --------------------------------------------------------------------------------------------------
http_archive(
    name = "rules_python",
    sha256 = "be04b635c7be4604be1ef20542e9870af3c49778ce841ee2d92fcb42f9d9516a",
    strip_prefix = "rules_python-0.35.0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.35.0/rules_python-0.35.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

load("@rules_python//python:pip.bzl", "pip_parse")
pip_parse(
    name = "pip_deps",
    requirements_lock = "//third_party/py:requirements.txt",
)
load("@pip_deps//:requirements.bzl", "install_deps")
install_deps()

# --------------------------------------------------------------------------------------------------
# rules_proto defines abstract rules for building Protocol Buffers
# --------------------------------------------------------------------------------------------------
http_archive(
    name = "rules_proto",
    sha256 = "6fb6767d1bef535310547e03247f7518b03487740c11b6c6adb7952033fe1295",
    strip_prefix = "rules_proto-6.0.2",
    url = "https://github.com/bazelbuild/rules_proto/releases/download/6.0.2/rules_proto-6.0.2.tar.gz",
)

load("@rules_proto//proto:repositories.bzl", "rules_proto_dependencies")
rules_proto_dependencies()

load("@rules_proto//proto:setup.bzl", "rules_proto_setup")
rules_proto_setup()

load("@rules_proto//proto:toolchains.bzl", "rules_proto_toolchains")
rules_proto_toolchains()

# --------------------------------------------------------------------------------------------------
# Protocol Buffers
# --------------------------------------------------------------------------------------------------
http_archive(
    name = "com_google_protobuf",
    sha256 = "4fc5ff1b2c339fb86cd3a25f0b5311478ab081e65ad258c6789359cd84d421f8",
    strip_prefix = "protobuf-26.1",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/v26.1.tar.gz"],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
protobuf_deps()

# --------------------------------------------------------------------------------------------------
# https://github.com/tehmaze/ipcalc.git
# --------------------------------------------------------------------------------------------------
new_git_repository(
    name = "ipcalc",
    tag = "ipcalc-1.99.0",
    remote = "https://github.com/tehmaze/ipcalc.git",
    build_file_content = """
py_library(
  name = "ipcalc",
  srcs = ["ipcalc.py"],
  visibility = ["//visibility:public"],
)
    """,
)

# --------------------------------------------------------------------------------------------------
# https://github.com/yaml/pyyaml.git
# --------------------------------------------------------------------------------------------------
new_git_repository(
    name = "pyyaml",
    tag = "6.0.2",
    remote = "https://github.com/yaml/pyyaml.git",
    strip_prefix = "lib/yaml",
    build_file_content = """
py_library(
  name = "pyyaml",
  srcs = glob(["*.py"]),
  visibility = ["//visibility:public"],
)
    """,
)

# --------------------------------------------------------------------------------------------------
# https://github.com/yaml/pyyaml.git
# --------------------------------------------------------------------------------------------------
new_git_repository(
    name = "absl-py",
    tag = "v2.1.0",
    remote = "https://github.com/abseil/abseil-py.git",
)
