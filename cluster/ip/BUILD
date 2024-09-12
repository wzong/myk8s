load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")
load("@rules_python//python:proto.bzl", "py_proto_library")

package(default_visibility = ["//visibility:public"])

proto_library(
    name = "ip_proto",
    srcs = ["ip.proto"],
    deps = ["//cluster/base:base_proto"],
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
      "//cluster/base",
      "@com_google_protobuf//:protobuf_python",
      "@ipcalc//:ipcalc",
      "@pyyaml//:pyyaml",
    ],
)

py_test(
    name = "ip_test",
    srcs = ["ip_test.py"],
    deps = [
      ":ip",
      "//cluster/base",
    ],
)
