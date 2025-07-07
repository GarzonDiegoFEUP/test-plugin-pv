from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class NewSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from test_plugin_pv.schema_packages.schema_package import m_package

        return m_package


class INLPackageEntryPoint(SchemaPackageEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from test_plugin_pv.schema_packages.INL_package import m_package

        return m_package


schema_package_entry_point = NewSchemaPackageEntryPoint(
    name='NewSchemaPackage',
    description='New schema package entry point configuration.',
)


INL_schema_package_entry_point = INLPackageEntryPoint(
    name='INLPackage',
    description='INL package entry point configuration.',
)
