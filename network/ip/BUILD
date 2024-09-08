load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")
load("@rules_python//python:proto.bzl", "py_proto_library")

proto_library(
    name = "ip_proto",
    srcs = ["ip.proto"],
    deps = ["//network/base:base_proto"],
)

py_proto_library(
    name = "ip_py_pb2",
    deps = [":ip_proto"],
)

py_library(
    name = "ip",
    srcs = ["ip.py"],
    deps = [
      ":ip_py_pb2",
      "//network/base",
      "@com_google_protobuf//:protobuf_python",
      "@ipcalc//:ipcalc",
    ],
)

py_test(
    name = "ip_test",
    srcs = ["ip_test.py"],
    deps = [
      ":ip",
      "//network/base",
    ],
)
