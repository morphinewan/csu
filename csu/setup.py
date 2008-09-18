from distutils.core import setup
import py2exe
setup(windows=['cs.py',
               {"script":"cs.py",
                "version":"0.5",
                "company_name":"morphinewan.com"}],
      data_files=[("Floss Map", ["flossmap.dat"]),])