from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class NewParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from test_plugin_pv.parsers.parser import NewParser

        return NewParser(**self.model_dump())


class INLExperimentParserEntryPoint(ParserEntryPoint):
    def load(self):
        from test_plugin_pv.parsers.INL_batch_parser import INLExperimentParser

        return INLExperimentParser(**self.model_dump())


class INLParserEntryPoint(ParserEntryPoint):
    def load(self):
        from test_plugin_pv.parsers.INL_measurement_parser import INLParser

        return INLParser(**self.model_dump())


parser_entry_point = NewParserEntryPoint(
    name='NewParser',
    description='New parser entry point configuration.',
    mainfile_name_re=r'.*\.newmainfilename',
)


INL_experiment_parser_entry_point = INLExperimentParserEntryPoint(
    name='INLExperimentParserEntryPoint',
    description='INL experiment parser entry point configuration.',
    mainfile_name_re='^(.+\.xlsx)$',
    mainfile_mime_re='(application|text|image)/.*',
)


INL_parser_entry_point = INLParserEntryPoint(
    name='INLParserEntryPoint',
    description='INL parser entry point configuration.',
    mainfile_name_re='^.+\.?.+\.((eqe|jv|mppt)\..{1,4})$',
    mainfile_mime_re='(application|text|image)/.*',
)
