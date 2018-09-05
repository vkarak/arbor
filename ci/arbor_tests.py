import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ArborBaseTest(rfm.RegressionTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['daint:gpu', 'daint:mc', 'tresa']
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-clang']
        self.sourcesdir = os.path.join(self.prefix, '..')
        self.executable = './build/bin/unit'
        if self.current_system.name.startswith('daint'):
            self.variables = {'CRAYPE_LINK_TYPE': 'dynamic'}

        self.sanity_patterns = sn.assert_found('PASSED', self.stdout)
        self.build_system = 'Make'
        self.build_system.flags_from_environ = False
        self.modules = ['CMake', 'gcc/7.1.0']
        self.tags = {'sanity'}

    def setup(self, partition, environ, **job_opts):
        config_opts = [
            '-DCMAKE_C_COMPILER=%s' % environ.cc,
            '-DCMAKE_CXX_COMPILER=%s' % environ.cxx
        ] + self.cmake_options
        self.prebuild_cmd = [
            'mkdir build',
            'cd build',
            'cmake .. %s' % ' '.join(config_opts)
        ]
        super().setup(partition, environ, **job_opts)

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON']


@rfm.simple_test
class ArborMPITest(ArborBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['daint:gpu', 'daint:mc']
        self.valid_prog_environs = ['PrgEnv-gnu']

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON',
                '-DARB_WITH_MPI=ON']


@rfm.simple_test
class ArborGpuTest(ArborBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['daint:gpu']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.modules += ['craype-accel-nvidia60']

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON',
                '-DARB_GPU_MODEL=P100']


@rfm.parameterized_test(['haswell'], ['broadwell'], ['native'])
class ArborSIMDTest(ArborBaseTest):
    def __init__(self, arch_kind):
        super().__init__()
        if arch_kind == 'haswell':
            self.valid_systems = ['daint:gpu']
        elif arch_kind == 'broadwell':
            self.valid_systems = ['daint:mc', 'tresa']
        elif arch_kind == 'native':
            self.valid_systems = ['tresa']

        self.arch_kind = arch_kind

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON',
                '-DARB_VECTORIZE=ON',
                '-DARB_ARCH=%s' % self.arch_kind]
