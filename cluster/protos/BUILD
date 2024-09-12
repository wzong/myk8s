load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:proto.bzl", "py_proto_library")

package(default_visibility = ["//visibility:public"])

proto_library(
    name = "base_proto",
    srcs = ["base.proto"],
)

py_proto_library(
    name = "base_py_pb2",
    deps = [":base_proto"],
)

proto_library(
    name = "ip_proto",
    srcs = ["ip.proto"],
    deps = [":base_proto"],
)

py_proto_library(
    name = "ip_py_pb2",
    deps = [":ip_proto"],
)

