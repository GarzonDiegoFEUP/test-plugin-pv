#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import random
import string

import numpy as np
import pandas as pd
from baseclasses import (
    BaseMeasurement,
    BaseProcess,
    Batch,
    LayerDeposition,
)
from baseclasses.helper.add_solar_cell import add_band_gap
from baseclasses.helper.utilities import get_encoding, set_sample_reference
from baseclasses.material_processes_misc import (
    Cleaning,
    LaserScribing,
    PlasmaCleaning,
    SolutionCleaning,
    Storage,
    UVCleaning,
)
from baseclasses.solar_energy import (
    EQEMeasurement,
    JVMeasurement,
    MPPTracking,
    SolcarCellSample,
    Substrate,
)
from baseclasses.solution import Solution, SolutionPreparationStandard
from baseclasses.vapour_based_deposition import (
    ALDPropertiesIris,
    AtomicLayerDeposition,
    Evaporations,
    Sputtering,
)
from baseclasses.voila import VoilaNotebook
from baseclasses.wet_chemical_deposition import (
    BladeCoating,
    DipCoating,
    LP50InkjetPrinting,
    SlotDieCoating,
    SpinCoating,
    SprayPyrolysis,
    WetChemicalDeposition,
)
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

m_package = SchemaPackage()


# %% ####################### Entities


def randStr(chars=string.ascii_uppercase + string.digits, N=6):
    return ''.join(random.choice(chars) for _ in range(N))


class INL_VoilaNotebook(VoilaNotebook, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


class INL_Substrate(Substrate, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'components', 'elemental_composition'],
            properties=dict(
                order=[
                    'name',
                    'substrate',
                    'conducting_material',
                    'solar_cell_area',
                    'pixel_area',
                    'number_of_pixels',
                ]
            ),
        )
    )


class INL_Solution(Solution, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users',
                'components',
                'elemental_composition',
                'method',
                'temperature',
                'time',
                'speed',
                'solvent_ratio',
                'washing',
            ],
            properties=dict(
                order=[
                    'name',
                    'datetime',
                    'lab_id',
                    'description',
                    'preparation',
                    'solute',
                    'solvent',
                    'other_solution',
                    'additive',
                    'storage',
                ],
            ),
        ),
        a_template=dict(temperature=45, time=15, method='Shaker'),
    )

    preparation = SubSection(section_def=SolutionPreparationStandard)


class INL_Sample(SolcarCellSample, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition'],
            properties=dict(order=['name', 'substrate', 'architecture']),
        ),
        a_template=dict(
            institute='INL_INL'),
        label_quantity='sample_id',
    )


class INL_Batch(Batch, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['users', 'samples'],
            properties=dict(order=['name', 'export_batch_ids', 'csv_export_file']),
        )
    )


# %% ####################### Cleaning
class INL_Cleaning(Cleaning, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )

    location = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    cleaning = SubSection(section_def=SolutionCleaning, repeats=True)
    cleaning_uv = SubSection(section_def=UVCleaning, repeats=True)
    cleaning_plasma = SubSection(section_def=PlasmaCleaning, repeats=True)


# %% ##################### Layer Deposition
class INL_SprayPyrolysis(SprayPyrolysis, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )


# %% ### Printing


class INL_Inkjet_Printing(LP50InkjetPrinting, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'recipe_used',
                    'print_head_used',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'print_head_path',
                    'nozzle_voltage_profile',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


# %% ### Spin Coating
class INL_SpinCoating(SpinCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
                'recipe',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'recipe',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
    )


# %% ### Dip Coating


class INL_DipCoating(DipCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
        a_template=dict(
            layer_type='Absorber Layer',
        ),
    )


class INL_BladeCoating(BladeCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )


# %% ### Slot Die Coating


class INL_SlotDieCoating(SlotDieCoating, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'author',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'properties',
                    'quenching',
                    'annealing',
                ]
            ),
        ),
    )


# %% ### Sputterring
class INL_Sputtering(Sputtering, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


# %% ### AtomicLayerDepositio
class INL_AtomicLayerDeposition(AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


class INL_AtomicLayerDeposition(AtomicLayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    properties = SubSection(section_def=ALDPropertiesIris)


# %% ### Evaporation
class INL_Evaporation(Evaporations, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )


# %% ## Laser Scribing
class INL_LaserScribing(LaserScribing, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'users', 'end_time', 'steps', 'instruments', 'results'],
            properties=dict(order=['name', 'location', 'present',
                            'datetime', 'batch', 'samples']),
        )
    )


# %% ## Storage


class INL_Storage(Storage, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'location',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                ]
            ),
        )
    )


# %%####################################### Measurements

class INL_JVmeasurement(JVMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'author',
                'certified_values',
                'certification_institute',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'data_file',
                    'active_area',
                    'intensity',
                    'integration_time',
                    'settling_time',
                    'averaging',
                    'compliance',
                    'samples',
                ]
            ),
        ),
        a_plot=[
            {
                'x': 'jv_curve/:/voltage',
                'y': 'jv_curve/:/current_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id,
                                 upload_id=archive.metadata.upload_id)
        if self.data_file:
            # todo detect file format
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                pass  # add parsing here

        super().normalize(archive, logger)


class INL_SimpleMPPTracking(MPPTracking, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'time',
                'y': 'power_density',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id,
                                 upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:
                pass  # add parsing here

        super().normalize(archive, logger)


class INL_EQEmeasurement(EQEMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'solution',
                'users',
                'location',
                'end_time',
                'steps',
                'instruments',
                'results',
                'data',
                'header_lines',
            ],
            properties=dict(order=['name', 'data_file', 'samples']),
        ),
        a_plot=[
            {
                'x': 'eqe_data/:/photon_energy_array',
                'y': 'eqe_data/:/eqe_array',
                'layout': {
                    'showlegend': True,
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False},
                },
            }
        ],
    )

    def normalize(self, archive, logger):
        eqe_data = []
        if not self.samples and self.data_file:
            search_id = self.data_file.split('.')[0]
            set_sample_reference(archive, self, search_id,
                                 upload_id=archive.metadata.upload_id)

        if self.data_file:
            with archive.m_context.raw_file(self.data_file, 'br') as f:
                encoding = get_encoding(f)
            with archive.m_context.raw_file(self.data_file, 'tr', encoding=encoding) as f:

                txt = ''
                lines = f.readlines()
                i=0
                line = lines[i]
                while line != 'end data\n':
                    txt += line
                    i +=1
                    line = lines[i]

                fil_data = open('data_'  + f.split('.txt')[0] + '.txt', 'w')
                fil_data.write(txt)
                fil_data.close()
                data = pd.read_csv('data_' + f.split('.txt')[0] + '.txt', sep='\t')
                eqe_data_new = EQEMeasurement()
                eqe_data_new.data.raw_eqe_array = data['QE'].values
                eqe_data_new.data.raw_wavelength_array = data['WL'].values
                eqe_data_new.data.raw_photon_energy_array = 1239.84193/(data['WL']+0.000001)

                eqe_data.append(eqe_data_new)

            if eqe_data:
                band_gaps = np.array([d.bandgap_eqe.magnitude for d in eqe_data])
                add_band_gap(archive, band_gaps[np.isfinite(band_gaps)].mean())

        super().normalize(archive, logger)


# %%####################################### Generic Entries


class ProcessParameter(ArchiveSection):
    m_def = Section(label_quantity='name')
    name = Quantity(
        type=str,
        description="""
        The name of a paramter.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )

    value_number = Quantity(
        type=np.dtype(np.float64),
        description="""
        The numerical value of a continous paramter.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    value_string = Quantity(
        type=str,
        description="""
        The string value of a categorical paramter.
        """,
        a_eln=dict(component='StringEditQuantity'),
    )


class INL_Process(BaseProcess, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=['name', 'present', 'data_file', 'batch', 'samples']),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    process_parameters = SubSection(section_def=ProcessParameter, repeats=True)


class INL_WetChemicalDeposition(WetChemicalDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'solution',
                    'layer',
                    'quenching',
                    'annealing',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class INL_Deposition(LayerDeposition, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(
                order=[
                    'name',
                    'present',
                    'datetime',
                    'previous_process',
                    'batch',
                    'samples',
                    'layer',
                ]
            ),
        )
    )

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


class INL_Measurement(BaseMeasurement, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id',
                'users',
                'end_time',
                'steps',
                'instruments',
                'results',
            ],
            properties=dict(order=['name', 'data_file', 'samples', 'solution']),
        )
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )


m_package.__init_metainfo__()
