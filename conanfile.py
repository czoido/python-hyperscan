from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class HyperscanPyConan(ConanFile):
    name = "python-hyperscan"
    version = "0.8.2"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    default_options = {
        "vectorscan/*:with_chimera": True,
        "hyperscan/*:build_chimera": True,
        # hyperscan/vectorscan only use boost.headers (graph, intrusive, etc.).
        # Skip components whose build deps don't always cross-compile cleanly
        # (locale needs iconv, stacktrace_backtrace needs libbacktrace native).
        "boost/*:without_locale": True,
        "boost/*:without_stacktrace_backtrace": True,
    }

    def layout(self):
        cmake_layout(self)

    def configure(self):
        if self.settings.os == "Windows":
            # On Windows, hyperscan's chimera is built referencing PCRE via
            # __declspec(dllimport) (no PCRE_STATIC defined upstream), so
            # chimera.lib expects pcre.dll's import library at link time.
            # Force pcre as shared to match. delvewheel bundles pcre.dll
            # into the wheel automatically.
            self.options["pcre/*"].shared = True

    def requirements(self):
        if self.settings.os == "Windows":
            # vectorscan upstream doesn't support MSVC; fall back to Intel
            # hyperscan, mirroring what the original CMakeLists.txt did.
            self.requires("hyperscan/5.4.2")
        else:
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
