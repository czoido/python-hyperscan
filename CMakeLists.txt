cmake_minimum_required(VERSION 3.20)
project(python_hyperscan LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# vectorscan upstream doesn't support MSVC; on Windows the conanfile pulls
# Intel's hyperscan instead.
if(WIN32)
    find_package(hyperscan REQUIRED)
    set(HS_CONAN_TARGET hyperscan::hyperscan)
else()
    find_package(vectorscan REQUIRED)
    set(HS_CONAN_TARGET vectorscan::vectorscan)
endif()

set(HS_EXT_NAME _hs_ext)
python_add_library(${HS_EXT_NAME} MODULE src/hyperscan/extension.c WITH_SOABI)

# vectorscan/chimera are C++ — force C++ linker for the extension.
set_target_properties(${HS_EXT_NAME} PROPERTIES
  POSITION_INDEPENDENT_CODE ON
  LINKER_LANGUAGE CXX)

if(WIN32)
  target_compile_options(${HS_EXT_NAME} PRIVATE /FS /GS-)
else()
  # Hide all symbols by default to prevent conflicts with other C++ extensions
  # (e.g. numpy, scipy, sklearn) that may use the same C++ runtime symbols.
  target_compile_options(${HS_EXT_NAME} PRIVATE
    -fPIC
    -D_GLIBCXX_USE_CXX11_ABI=1
    -fvisibility=hidden
    -fvisibility-inlines-hidden
  )
  target_link_options(${HS_EXT_NAME} PRIVATE -O0)
endif()

target_link_libraries(${HS_EXT_NAME} PRIVATE Python::Module ${HS_CONAN_TARGET})

if("$ENV{AUDITWHEEL_PLAT}" MATCHES "musllinux")
  target_link_options(${HS_EXT_NAME} PRIVATE
    -Wl,-s
    -Wl,--gc-sections
    -Wl,--exclude-libs,ALL
    -static-libgcc
    -Wl,--whole-archive
    -l:libstdc++.a
    -Wl,--no-whole-archive
  )
elseif(APPLE)
  target_link_libraries(${HS_EXT_NAME} PRIVATE c++)
elseif(NOT WIN32)
  if("$ENV{AUDITWHEEL_PLAT}" MATCHES "manylinux2014")
    target_link_options(${HS_EXT_NAME} PRIVATE
      -Wl,--no-as-needed
      -Wl,--copy-dt-needed-entries
      -Wl,--no-allow-shlib-undefined
      -Wl,--exclude-libs,ALL
    )
    target_link_libraries(${HS_EXT_NAME} PRIVATE -Wl,--push-state -Wl,-Bstatic -lstdc++ -Wl,--pop-state)
  else()
    target_link_options(${HS_EXT_NAME} PRIVATE
      -Wl,--no-as-needed
      -Wl,--exclude-libs,ALL
    )
    target_link_libraries(${HS_EXT_NAME} PRIVATE stdc++)
  endif()
endif()

install(
  TARGETS ${HS_EXT_NAME}
  LIBRARY
  DESTINATION hyperscan
  COMPONENT hyperscan
)
