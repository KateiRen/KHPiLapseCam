import re
import time

class Wrapper(object):

    def __init__(self, subprocess):
        self._subprocess = subprocess

    def call(self, cmd):
        p = self._subprocess.Popen(cmd, shell=True, stdout=self._subprocess.PIPE,
            stderr=self._subprocess.PIPE)
        out, err = p.communicate()
        return p.returncode, out.rstrip(), err.rstrip()



class Identify(Wrapper):
    """ A class which wraps calls to the external identify process. """

    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)
        self._CMD = 'identify'

    def summary(self, filepath):
        code, out, err = self.call(self._CMD + " " + filepath)
        if code != 0:
            raise Exception(err)
        return out

    def mean_brightness(self, filepath):
        code, out, err = self.call(self._CMD + ' -format "%[mean]" ' + filepath)
        if code != 0:
            raise Exception(err)
        return out

