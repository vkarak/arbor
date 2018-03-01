import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RegressionTest


class ArborBaseTest(RegressionTest):
    def __init__(self, **kwargs):
        super().__init__('arbor_base_test', os.path.dirname(__file__), **kwargs)
        self.valid_systems = ['daint:gpu', 'daint:mc', 'dom:gpu', 'dom:mc']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.sourcesdir = os.path.join(self.prefix, '../..')
        self.sourcepath = 'build'
        self.prebuild_cmd = ['mkdir build', 'cd build && cmake ..']
        self.executable = './build/tests/test.exe'
        self.variables = {'CRAYPE_LINK_TYPE': 'dynamic'}
        self.sanity_patterns = sn.assert_found('PASSED', self.stdout)

    def compile(self):
        self.current_environ.propagate = False
        super().compile(options='-j')


class ArborMPITest(ArborBaseTest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'arbor_mpi_test'
        self.prebuild_cmd = ['mkdir build',
                             'cd build && cmake .. -DARB_WITH_MPI=ON']


class ArborTBBTest(ArborBaseTest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'arbor_tbb_test'
        self.prebuild_cmd = ['mkdir build',
                             'cd build && cmake .. -DARB_THREADING_MODEL=tbb']


def _get_checks(**kwargs):
    return [ArborBaseTest(**kwargs),
            ArborMPITest(**kwargs),
            ArborTBBTest(**kwargs)]
