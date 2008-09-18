from distutils.core import setup
import py2exe
setup(windows=['CrossStitchMakerGUI.py',
               {"script":"CrossStitchMakerGUI.py",
                "version":"1.0",
                "company_name":"morphinewan.com",
                "icon_resources":[(1, "favicon.ico")]}],
      data_files=[("Color_Table", ["Color_Table/DMC.txt"]),])