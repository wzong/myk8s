load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")
load("@rules_python//python:proto.bzl", "py_proto_library")

proto_library(
    name = "router_proto",
    srcs = ["router.proto"],
    deps = ["//network/base:base_proto"],
)

py_proto_library(
    name = "router_py_pb2",
    deps = [":router_proto"],
)

py_library(
    name = "router",
    srcs = ["router.py"],
    deps = [
      ":router_py_pb2",
      "//network/base",
      "@com_google_protobuf//:protobuf_python",
      "@ipcalc//:ipcalc",
      "@pyyaml//:pyyaml",
    ],
)

py_test(
    name = "router_test",
    srcs = ["router_test.py"],
    deps = [
      ":router",
      "//network/base",
    ],
)
