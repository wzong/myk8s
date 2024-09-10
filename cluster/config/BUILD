load("@rules_proto//proto:defs.bzl", "proto_library")
load("@rules_python//python:proto.bzl", "py_proto_library")

proto_library(
    name = "config_proto",
    srcs = ["config.proto"],
    deps = ["//cluster/ip:ip_proto"],
)

py_proto_library(
    name = "config_py_pb2",
    deps = [":config_proto"],
)
