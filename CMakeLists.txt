cmake_minimum_required(VERSION 3.16.3...3.28 FATAL_ERROR)

project(Slicer_ASLtoolkit)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/Slicer_ASLtoolkit")
set(EXTENSION_CATEGORY "Arterial Sping Labelling")
set(EXTENSION_CONTRIBUTORS "Antonio Senra Filho (State University of Campinas), Andre M. Paschoal (State University of Campinas)")
set(EXTENSION_DESCRIPTION "This extension offers image processing techniques for Arterial Sping Labeling (ASL) MRI imaging.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/Slicer_ASLtoolkit.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/Slicer_ASLtoolkit/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CBF_ATT_ASL)
add_subdirectory(Multi_Echo_ASL)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
