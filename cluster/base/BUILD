load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:defs.bzl", "py_library", "py_test")
load("@rules_python//python:proto.bzl", "py_proto_library")
load("@pip_deps//:requirements.bzl", "requirement")

package(default_visibility=["//visibility:public"])

py_library(
    name = "base",
    srcs = ["base.py"],
    deps = [
      "//cluster/protos:base_py_pb2",
      requirement("psutil"),
    ],
)

py_test(
    name = "base_test",
    srcs = ["base_test.py"],
    deps = [":base"],
)
