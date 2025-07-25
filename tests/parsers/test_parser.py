import os

from nomad.client import parse
from nomad.units import ureg
from utils import delete_json


def test_batch_parser(monkeypatch):  # noqa: PLR0915
    file = '20250114_experiment_file.xlsx'
    file_name = os.path.join('tests', 'data', file)
    file_archive = parse(file_name)[0]
    assert len(file_archive.data.processed_archive) == 27

    measurement_archives = []
    for file in os.listdir(os.path.join('tests', 'data')):
        if 'archive.json' not in file:
            continue
        measurement = os.path.join('tests', 'data', file)
        measurement_archives.append(parse(measurement)[0])
    measurement_archives.sort(key=lambda x: x.metadata.mainfile)

    count_samples_batches = 0
    for m in measurement_archives:
        if 'Sample' in str(type(m.data)) or 'Batch' in str(type(m.data)):
            count_samples_batches += 1
            if 'Sample' in str(type(m.data)):
                assert m.data.description == 'A'
                assert m.data.number_of_junctions == 1
        elif 'Substrate' in str(type(m.data)):
            assert m.data.solar_cell_area == 10 * ureg('cm**2')
            assert m.data.pixel_area == 0.16 * ureg('cm**2')
            assert m.data.number_of_pixels == 6
            assert m.data.description == 'Normal'
            assert m.data.substrate == 'Glass'
            assert m.data.conducting_material[0] == 'ITO'

        elif m.data.positon_in_experimental_plan == 1:
            assert 'Cleaning' in str(type(m.data))
            assert m.data.cleaning[0].time == 100 * ureg('s')
            assert m.data.cleaning[0].temperature == ureg.Quantity(10, ureg('°C'))
            assert m.data.cleaning[0].solvent_2.name == 'Isopropanol'
            assert m.data.cleaning[1].time == 10 * ureg('minute')
            assert m.data.cleaning[1].temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.cleaning[1].solvent_2.name == 'Ethanol'
            assert m.data.cleaning_plasma[0].time == 20 * ureg('s')
            assert m.data.cleaning_plasma[0].power == 50 * ureg('W')
            assert m.data.cleaning_plasma[0].plasma_type == 'O2'

        elif m.data.positon_in_experimental_plan == 2:
            assert 'SpinCoating' in str(type(m.data))
            assert m.data.description == 'Bla'
            assert m.data.layer[0].layer_type == 'Absorber Layer'
            assert m.data.layer[0].layer_material_name == 'CsMAFA'
            assert m.data.annealing.temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.annealing.atmosphere == 'Ar'
            assert m.data.annealing.time == 10 * ureg('minute')
            assert m.data.solution[0].solution_volume == (1 * ureg('uL')).to('ml')
            assert (
                m.data.solution[0].solution_details.solvent[0].chemical_2.name
                == 'Ethanol'
            )
            assert m.data.solution[0].solution_details.solvent[0].chemical_volume == (
                1 * ureg('uL')
            ).to('ml')
            assert m.data.solution[0].solution_details.solvent[0].amount_relative == 1
            assert (
                m.data.solution[0].solution_details.solute[0].chemical_2.name == 'PbI2'
            )
            assert m.data.solution[0].solution_details.solute[
                0
            ].concentration_mass == 2 * ureg('mg/ml')
            assert m.data.solution[0].solution_details.solute[0].amount_relative == 0.5
            assert m.data.recipe_steps[0].speed == 100 * ureg('rpm')
            assert m.data.recipe_steps[0].time == 10 * ureg('s')
            assert m.data.recipe_steps[0].acceleration == 100 * ureg('rpm/s')
            assert m.data.recipe_steps[1].speed == 10 * ureg('rpm')
            assert m.data.recipe_steps[1].time == 100 * ureg('s')
            assert m.data.recipe_steps[1].acceleration == 10 * ureg('rpm/s')
            assert m.data.quenching.anti_solvent_volume == 10 * ureg('ml')
            assert m.data.quenching.anti_solvent_dropping_time == 15 * ureg('s')
            assert m.data.quenching.anti_solvent_dropping_height == 10 * ureg('mm')
            assert m.data.quenching.anti_solvent_dropping_flow_rate == 100 * ureg(
                'uL/s'
            )
            assert m.data.quenching.anti_solvent_2.name == 'Ethanol'

        elif m.data.positon_in_experimental_plan == 3:
            assert 'Inkjet' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'HTL'
            assert m.data.layer[0].layer_material_name == 'NiO2'
            assert m.data.solution[0].solution_details.solute[0].chemical_2.name == 'Ni'
            assert m.data.annealing.temperature == ureg.Quantity(14, ureg('°C'))
            assert m.data.annealing.atmosphere == 'N2'
            assert m.data.annealing.time == 100 * ureg('minute')
            assert (
                m.data.properties.print_head_properties.number_of_active_print_nozzles
                == 10
            )
            assert (
                m.data.properties.print_head_properties.print_nozzle_drop_frequency
                == 10 * ureg('1/s')
            )
            assert (
                m.data.properties.print_head_properties.print_nozzle_drop_volume
                == 10 * ureg('pL')
            )
            assert (
                m.data.properties.print_head_properties.print_head_temperature
                == ureg.Quantity(10, ureg('°C'))
            )
            assert m.data.properties.print_head_properties.print_head_name == 'abc'
            assert m.data.properties.cartridge_pressure == ureg.Quantity(
                1, ureg('bar')
            ).to('mbar')
            assert m.data.properties.substrate_temperature == ureg.Quantity(
                500, ureg('°C')
            )
            assert m.data.properties.drop_density == 1 * ureg('1/in')
            assert m.data.properties.printed_area == 5 * ureg('mm**2')
            assert m.data.print_head_path.quality_factor == 'QF3'
            assert m.data.print_head_path.step_size == 'SS1'
            assert m.data.atmosphere.relative_humidity == 23

        elif m.data.positon_in_experimental_plan == 4:
            assert 'Atomic' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'ETL'
            assert m.data.layer[0].layer_material_name == 'Ar'
            assert m.data.properties.source == 'aa'
            assert m.data.properties.thickness == 10 * ureg('nm')
            assert m.data.properties.temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.properties.rate == 1 * ureg('angstrom/s')
            assert m.data.properties.time == 12 * ureg('s')
            assert m.data.properties.number_of_cycles == 10
            assert m.data.properties.material.material.name == '1'
            assert m.data.properties.material.pulse_duration == 12 * ureg('s')
            assert m.data.properties.material.manifold_temperature == ureg.Quantity(
                12, ureg('°C')
            )
            assert m.data.properties.material.bottle_temperature == ureg.Quantity(
                12, ureg('°C')
            )
            assert m.data.properties.oxidizer_reducer.material.name == '2'
            assert m.data.properties.oxidizer_reducer.pulse_duration == 2 * ureg('s')
            assert (
                m.data.properties.oxidizer_reducer.manifold_temperature
                == ureg.Quantity(3, ureg('°C'))
            )

        elif m.data.positon_in_experimental_plan == 5:
            assert 'Laser' in str(type(m.data))
            assert m.data.properties.laser_wavelength == 400 * ureg('nm')
            assert m.data.properties.laser_pulse_time == 10 * ureg('ps')
            assert m.data.properties.laser_pulse_frequency == 1 * ureg('kHz')
            assert m.data.properties.speed == 12 * ureg('mm/s')
            assert m.data.properties.fluence == 12 * ureg('J/cm**2')
            assert m.data.properties.power_in_percent == 3

        elif m.data.positon_in_experimental_plan == 6:
            assert 'SlotDie' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Absorber Layer'
            assert m.data.layer[0].layer_material_name == 'CsMaFa'
            assert m.data.annealing.temperature == ureg.Quantity(5, ureg('°C'))
            assert m.data.annealing.atmosphere == 'N2'
            assert m.data.annealing.time == 2 * ureg('minute')
            assert m.data.properties.flow_rate == (12 * ureg('uL/minute')).to(
                'ml/minute'
            )
            assert m.data.properties.slot_die_head_distance_to_thinfilm == 4 * ureg(
                'mm'
            )
            assert m.data.properties.slot_die_head_speed == 2 * ureg('mm/s')
            assert m.data.quenching.air_knife_angle == 1 * ureg('°')
            assert m.data.quenching.bead_volume == 12 * ureg('mm/s')
            assert m.data.quenching.drying_speed == 12 * ureg('cm/minute')
            assert m.data.quenching.air_knife_distance_to_thin_film == (
                1 * ureg('cm')
            ).to('um')

        elif m.data.positon_in_experimental_plan == 7:
            assert 'Evaporation' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'Electron Transport Layer'
            assert m.data.layer[0].layer_material_name == 'Ar'
            assert m.data.inorganic_evaporation
            assert m.data.inorganic_evaporation[0].thickness == 10 * ureg('nm')
            assert m.data.inorganic_evaporation[0].pressure == (10 * ureg('bar')).to(
                'mbar'
            )
            assert m.data.inorganic_evaporation[0].pressure_start == 1 * ureg('mbar')
            assert m.data.inorganic_evaporation[0].pressure_end == 2 * ureg('mbar')
            assert m.data.inorganic_evaporation[0].tooling_factor is None
            assert m.data.inorganic_evaporation[
                0
            ].substrate_temparature == ureg.Quantity(50, ureg('°C'))
            assert m.data.inorganic_evaporation[0].start_rate == 0.1 * ureg(
                'angstrom/s'
            )
            assert m.data.inorganic_evaporation[0].target_rate == 1.5 * ureg(
                'angstrom/s'
            )
            assert m.data.inorganic_evaporation[0].temparature[0] == ureg.Quantity(
                100, ureg('°C')
            )
            assert m.data.inorganic_evaporation[0].temparature[1] == ureg.Quantity(
                120, ureg('°C')
            )
        elif m.data.positon_in_experimental_plan == 8:
            assert 'Sputtering' in str(type(m.data))
            assert m.data.layer[0].layer_type == 'HTL'
            assert m.data.layer[0].layer_material_name == 'Pd'
            assert m.data.processes[0].thickness == 10 * ureg('nm')
            assert m.data.processes[0].gas_flow_rate == 1 * ureg('cm**3/minute')
            assert m.data.processes[0].rotation_rate == 100 * ureg('rpm')
            assert m.data.processes[0].power == 23 * ureg('W')
            assert m.data.processes[0].temperature == ureg.Quantity(100, ureg('°C'))
            assert m.data.processes[0].deposition_time == 12 * ureg('s')
            assert m.data.processes[0].burn_in_time == 1 * ureg('s')
            assert m.data.processes[0].pressure == 1 * ureg('mbar')
            assert m.data.processes[0].target_2.name == 'Pd'
            assert m.data.processes[0].gas_2.name == 'N2'

        elif m.data.positon_in_experimental_plan == 9:
            assert 'Process' in str(type(m.data))
            assert m.data.name == 'Another process'

        else:
            assert False

    assert count_samples_batches == 17
    delete_json()
