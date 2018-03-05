import os

import reframe.utility.sanity as sn
from reframe.core.pipeline import RegressionTest


class ArborBaseTest(RegressionTest):
    def __init__(self, name='arbor_base_test', **kwargs):
        super().__init__(name, os.path.dirname(__file__), **kwargs)
        self.valid_systems = ['daint:gpu', 'daint:mc', 'dom:gpu', 'dom:mc']
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel']
        self.sourcesdir = os.path.join(self.prefix, '../..')
        self.sourcepath = 'build'
        self.prebuild_cmd = ['mkdir build', 'cd build && cmake ..']
        self.executable = './build/tests/test.exe'
        self.variables = {'CRAYPE_LINK_TYPE': 'dynamic'}
        self.sanity_patterns = sn.assert_found('PASSED', self.stdout)
        self.prebuild_cmd = [
            'mkdir build',
            'cd build && cmake .. %s' % ' '.join(self.cmake_options)
        ]
        self.modules = ['gcc/7.1.0']

    @property
    def cmake_options(self):
        return ['-DARB_WITH_ASSERTIONS=ON']

    def compile(self):
        self.current_environ.propagate = False
        super().compile(options='-j')


class ArborMPITest(ArborBaseTest):
    def __init__(self, **kwargs):
        super().__init__(name='arbor_mpi_test', **kwargs)

    @property
    def cmake_options(self):
        return ['-DARB_WITH_MPI=ON']


class ArborTBBTest(ArborBaseTest):
    def __init__(self, **kwargs):
        super().__init__(name='arbor_tbb_test', **kwargs)

    @property
    def cmake_options(self):
        return ['-DARB_THREADING_MODEL=tbb']


class ArborCThreadTest(ArborBaseTest):
    def __init__(self, **kwargs):
        super().__init__(name='arbor_cthread_test', **kwargs)

    @property
    def cmake_options(self):
        return ['-DARB_THREADING_MODEL=cthread']


class ArborCudaTest(ArborBaseTest):
    def __init__(self, **kwargs):
        super().__init__('arbor_cuda_test', **kwargs)
        self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.modules += ['cudatoolkit']

    @property
    def cmake_options(self):
        return ['-DARB_WITH_CUDA=ON']


class ArborSIMDTest(ArborBaseTest):
    def __init__(self, simd_kind, **kwargs):
        self.simd_kind = simd_kind
        super().__init__('arbor_%s_test' % simd_kind, **kwargs)

    @property
    def cmake_options(self):
        return ['-DARB_VECTORIZE_TARGET=%s' % self.simd_kind.upper()]


def _get_checks(**kwargs):
    return [ArborBaseTest(**kwargs),
            ArborMPITest(**kwargs),
            ArborTBBTest(**kwargs),
            ArborCThreadTest(**kwargs),
            ArborCudaTest(**kwargs),
            ArborSIMDTest('avx2', **kwargs)]
