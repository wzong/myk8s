load("@rules_python//python:defs.bzl", "py_library", "py_test")

py_library(
  name = "loadbalancer",
  srcs = ["loadbalancer.py"],
  deps = [
    "//cluster/base",
    "//cluster/ip",
  ]
)

py_test(
  name = "loadbalancer_test",
  srcs = ["loadbalancer_test.py"],
  deps = [
    ":loadbalancer",
    "//cluster/base",
    "//cluster/ip",
    "//cluster/protos:ip_py_pb2",
  ]
)
