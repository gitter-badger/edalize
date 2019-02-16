import pytest

def test_vcs2():
    import os
    import shutil
    from edalize_common import compare_files, setup_backend, tests_dir

    ref_dir      = os.path.join(tests_dir, __name__)
    paramtypes   = ['plusarg', 'vlogdefine', 'vlogparam']
    name         = 'test_vcs_0'
    tool         = 'vcs'
    tool_options = {}
#    tool_options = {
#        'iverilog_options' : ['some', 'iverilog_options'],
#        'timescale'        : '1ns/1ns',
#    }

    (backend, args, work_root) = setup_backend(paramtypes, name, tool, tool_options, use_vpi=False)
    backend.configure(args)

    compare_files(ref_dir, work_root, ['Makefile',
                                       name+'.scr',
    ])

    backend.build()
    compare_files(ref_dir, work_root, ['vcs.cmd'])

    backend.run(args)

    compare_files(ref_dir, work_root, ['run.cmd'])

def test_vcs_minimal():
    import os
    import shutil
    import tempfile

    from edalize import get_edatool

    from edalize_common import compare_files, tests_dir

    ref_dir      = os.path.join(tests_dir, __name__, 'minimal')
    os.environ['PATH'] = os.path.join(tests_dir, 'mock_commands')+':'+os.environ['PATH']
    tool = 'vcs'
    name = 'test_'+tool+'_minimal_0'
    work_root = tempfile.mkdtemp(prefix=tool+'_')

    edam = {'name'         : name,
               'toplevel' : 'top'}

    backend = get_edatool(tool)(edam=edam, work_root=work_root)
    backend.configure([])

    compare_files(ref_dir, work_root, ['Makefile',
                                       name+'.scr',
    ])

    backend.build()
    compare_files(ref_dir, work_root, ['vcs.cmd'])

    backend.run([])

    compare_files(ref_dir, work_root, ['run.cmd'])
