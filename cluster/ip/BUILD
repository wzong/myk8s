load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")
load("@rules_python//python:proto.bzl", "py_proto_library")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "ip",
    srcs = ["ip.py"],
    deps = [
      "//cluster/base",
      "//cluster/protos:ip_py_pb2",
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
