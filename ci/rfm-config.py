#
# CSCS ReFrame settings
#


class ReframeSettings:
    reframe_module = 'reframe'
    job_poll_intervals = [1, 2, 3]
    job_submit_timeout = 60
    checks_path = ['checks/']
    checks_path_recurse = True
    site_configuration = {
        'systems': {
            'daint': {
                'descr': 'Piz Daint compute nodes',
                'hostnames': ['daint'],
                'modules_system': 'tmod',
                'partitions': {
                    'gpu': {
                        'scheduler': 'local+srun',
                        'modules': ['daint-gpu'],
                        'environs': ['PrgEnv-cray', 'PrgEnv-gnu',
                                     'PrgEnv-intel', 'PrgEnv-pgi'],
                        'descr': 'Hybrid nodes (Haswell/P100)',
                        'max_jobs': 100,
                    },
                    'mc': {
                        'scheduler': 'local+srun',
                        'modules': ['daint-mc'],
                        'environs': ['PrgEnv-cray', 'PrgEnv-gnu',
                                     'PrgEnv-intel', 'PrgEnv-pgi'],
                        'descr': 'Multicore nodes (Broadwell)',
                    }
                }
            },
            'tresa': {
                'descr': 'My Mac',
                'hostnames': ['tresa'],
                'partitions': {
                    'login': {
                        'scheduler': 'local',
                        'environs': ['PrgEnv-clang'],
                        'descr': 'My Mac',
                    }
                }
            }
        },
        'environments': {
            'tresa': {
                'PrgEnv-clang': {
                    'type': 'ProgEnvironment',
                    'cc': 'clang',
                    'cxx': 'clang++',
                    'ftn': None
                }
            },
            '*': {
                'PrgEnv-cray': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-cray'],
                },

                'PrgEnv-gnu': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-gnu'],
                },

                'PrgEnv-intel': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-intel'],
                },

                'PrgEnv-pgi': {
                    'type': 'ProgEnvironment',
                    'modules': ['PrgEnv-pgi'],
                },

                'builtin': {
                    'type': 'ProgEnvironment',
                    'cc':  'cc',
                    'cxx': '',
                    'ftn': '',
                },

                'builtin-gcc': {
                    'type': 'ProgEnvironment',
                    'cc':  'gcc',
                    'cxx': 'g++',
                    'ftn': 'gfortran',
                }
            }
        }
    }

    logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'file',
                'name': 'reframe.log',
                'level': 'DEBUG',
                'format': '[%(asctime)s] %(levelname)s: '
                          '%(check_info)s: %(message)s',
                'append': False,
            },

            # Output handling
            {
                'type': 'stream',
                'name': 'stdout',
                'level': 'INFO',
                'format': '%(message)s'
            },
            {
                'type': 'file',
                'name': 'reframe.out',
                'level': 'INFO',
                'format': '%(message)s',
                'append': False,
            }
        ]
    }

    perf_logging_config = {
        'level': 'DEBUG',
        'handlers': [
            #@ {
            #@     'type': 'graylog',
            #@     'host': 'your-server-here',
            #@     'port': 12345,
            #@     'level': 'INFO',
            #@     'format': '%(message)s',
            #@     'extras': {
            #@         'facility': 'reframe',
            #@         'data-version': '1.0',
            #@     }
            #@ },
            {
                'type': 'filelog',
                'prefix': '%(check_system)s/%(check_partition)s',
                'level': 'INFO',
                'format': (
                    '%(asctime)s|reframe %(version)s|'
                    '%(check_info)s|jobid=%(check_jobid)s|'
                    '%(check_perf_var)s=%(check_perf_value)s|'
                    'ref=%(check_perf_ref)s '
                    '(l=%(check_perf_lower_thres)s, '
                    'u=%(check_perf_upper_thres)s)'
                ),
                'append': True
            }
        ]
    }


settings = ReframeSettings()
