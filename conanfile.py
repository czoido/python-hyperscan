from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class HyperscanPyConan(ConanFile):
    name = "python-hyperscan"
    version = "0.8.2"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    default_options = {
        "vectorscan/*:with_chimera": True,
    }

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("vectorscan/5.4.11")

    def build_requirements(self):
        self.tool_requires("ragel/6.10")
        self.tool_requires("cmake/[>=3.31]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
