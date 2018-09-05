import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ArborBaseTest(rfm.RegressionTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['daint:gpu', 'daint:mc', 'dom:gpu', 'dom:mc']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.sourcesdir = os.path.join(self.prefix, '..')
        self.executable = './build/bin/unit'
        self.variables = {'CRAYPE_LINK_TYPE': 'dynamic'}
        self.sanity_patterns = sn.assert_found('PASSED', self.stdout)
        self.build_system = 'Make'
        self.build_system.flags_from_environ = False
        self.prebuild_cmd = [
            'mkdir build',
            'cd build',
            'cmake .. %s' % ' '.join(self.cmake_options)
        ]
        self.modules = ['CMake', 'gcc/7.1.0']
        self.tags = {'sanity'}

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON']


@rfm.simple_test
class ArborMPITest(ArborBaseTest):
    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON',
                '-DARB_WITH_MPI=ON']


@rfm.simple_test
class ArborGpuTest(ArborBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.modules += ['craype-accel-nvidia60']

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON',
                '-DARB_GPU_MODEL=P100']


@rfm.parameterized_test(['haswell'], ['broadwell'])
class ArborSIMDTest(ArborBaseTest):
    def __init__(self, arch_kind):
        self.arch_kind = arch_kind
        super().__init__()
        if arch_kind == 'haswell':
            self.valid_systems = ['daint:gpu']
        elif arch_kind == 'broadwell':
            self.valid_systems = ['daint:mc']
        else:
            self.valid_systems = []

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON',
                '-DARB_VECTORIZE=ON',
                '-DARB_ARCH=%s' % self.arch_kind]
