import os
import logging

from edalize.edatool import Edatool

logger = logging.getLogger(__name__)

class Isim(Edatool):

    tool_options = {'lists' : {'fuse_options' : 'String',
                               'isim_options' : 'String'}}

    argtypes = ['plusarg', 'vlogdefine', 'vlogparam']

    MAKEFILE_TEMPLATE="""#Auto generated by Edalize
include config.mk

all: $(TARGET)

$(TARGET):
	fuse $(TOPLEVEL) -prj $(TARGET).prj -o $(TARGET) $(VLOG_DEFINES) $(VLOG_INCLUDES) $(VLOG_PARAMS) $(FUSE_OPTIONS)

run: $(TARGET)
	./$(TARGET) -tclbatch run_$(TARGET).tcl $(ISIM_OPTIONS) $(EXTRA_OPTIONS)

run-gui: $(TARGET)
	./$(TARGET) -gui $(ISIM_OPTIONS) $(EXTRA_OPTIONS)
"""

    CONFIG_MK_TEMPLATE = """#Auto generated by Edalize
TARGET        = {target}
TOPLEVEL      = {toplevel}

VLOG_DEFINES  = {vlog_defines}
VLOG_INCLUDES = {vlog_includes}
VLOG_PARAMS   = {vlog_params}

FUSE_OPTIONS  =	{fuse_options}
ISIM_OPTIONS  =	{isim_options}

EXTRA_OPTIONS ?= {extra_options}
"""

    RUN_TCL_TEMPLATE = """#Auto generated by Edalize
wave log -r /
run all
quit
"""

    def configure_main(self):
        #Check if any VPI modules are present and display warning
        if len(self.vpi_modules) > 0:
            modules = [m['name'] for m in self.vpi_modules]
            logger.error('VPI modules not supported by Isim: %s' % ', '.join(modules))

        with open(os.path.join(self.work_root, self.name+'.prj'),'w') as f:
            (src_files, self.incdirs) = self._get_fileset_files()

            for src_file in src_files:
                prefix = ""
                logical_name = ""
                if src_file.file_type in [
                        "verilogSource",
                        "verilogSource-95",
                        "verilogSource-2001"]:
                    prefix = 'verilog'
                elif src_file.file_type.startswith("vhdlSource"):
                    prefix = 'vhdl'
                    if src_file.logical_name:
                        logical_name = src_file.logical_name + ' '
                elif src_file.file_type in ["systemVerilogSource",
                                            "systemVerilogSource-3.0",
                                            "systemVerilogSource-3.1",
                                            "systemVerilogSource-3.1a",
                                            "verilogSource-2005"]:
                    prefix = 'sv'
                elif src_file.file_type in ["user"]:
                    pass
                else:
                    _s = "{} has unknown file type '{}'"
                    logger.warning(_s.format(src_file.name,
                               src_file.file_type))
                if prefix:
                    f.write('{} work {}{}\n'.format(prefix, logical_name, src_file.name))

        with open(os.path.join(self.work_root, 'run_'+self.name+'.tcl'),'w') as f:
            f.write(self.RUN_TCL_TEMPLATE)

        with open(os.path.join(self.work_root, 'Makefile'),'w') as f:
            f.write(self.MAKEFILE_TEMPLATE)

        with open(os.path.join(self.work_root, 'config.mk'),'w') as f:
            vlog_defines  = ' '.join(['--define {}={}'.format(k, self._param_value_str(v)) for k,v, in self.vlogdefine.items()])
            vlog_includes = ' '.join(['-i '+k for k in self.incdirs])
            vlog_params   = ' '.join(['--generic_top {}={}'.format(k, self._param_value_str(v)) for k,v, in self.vlogparam.items()])
            fuse_options = ' '.join(self.tool_options.get('fuse_options', []))
            isim_options = ' '.join(self.tool_options.get('isim_options', []))

            _s = '-testplusarg {}={}'
            extra_options = ' '.join([_s.format(k, self._param_value_str(v)) for k,v in self.plusarg.items()])
            f.write(self.CONFIG_MK_TEMPLATE.format(target        = self.name,
                                                   toplevel      = self.toplevel,
                                                   vlog_defines  = vlog_defines,
                                                   vlog_includes = vlog_includes,
                                                   vlog_params   = vlog_params,
                                                   fuse_options  = fuse_options,
                                                   isim_options  = isim_options,
                                                   extra_options = extra_options))

    def run_main(self):
        args = ['run']
        # Plusargs
        if self.plusarg:
            _s = '-testplusarg {}={}'
            args.append('EXTRA_OPTIONS='+' '.join([_s.format(k, self._param_value_str(v)) for k,v in self.plusarg.items()]))
        self._run_tool('make', args)
